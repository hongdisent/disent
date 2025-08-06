
/*******************************************************************************
* Name        : minishell.c
* Author      : George K Oliynyk
* Pledge      : I pledge my honor that I have abided by the Stevens Honor System
******************************************************************************/
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <linux/limits.h>
#include <pwd.h>
#include <errno.h>
#include <dirent.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <libgen.h>

#define BLUE "\x1b[34;1m"
#define DEFAULT "\x1b[0m"

#define EMPTY 0
#define CD 1
#define EXIT 2
#define PWD 3
#define LF 4
#define LP 5
#define EXEC 6

#define T_CONTINUE 0
#define T_EXIT 1

volatile sig_atomic_t interrupted = 0;

int getCmd(char command[])
{
  if(!command) {return EMPTY;}
  if(!strcmp(command, "cd")) {return CD;}
  if(!strcmp(command, "exit")) {return EXIT;}
  if(!strcmp(command, "pwd")) {return PWD;}
  if(!strcmp(command, "lf")) {return LF;}
  if(!strcmp(command, "lp")) {return LP;}
  return EXEC;
}

int runShellCMD(int command, char* args[])
{
    struct passwd* ourPWD;
    struct dirent* direntry;
    struct stat* curStat = malloc(sizeof(struct stat));
    FILE* fp;
    DIR* dr;
    pid_t childPID;
    char placedir[PATH_MAX], cwd[PATH_MAX], cmdline[PATH_MAX];
    int status, maxLength;

    switch(command)
    {
        case(CD):
          if(args[2]) {fprintf(stderr, "Error: Too many arguments to cd.\n"); break;}
          ourPWD = getpwuid(getuid());
          if(!ourPWD) {fprintf(stderr, "Error: Cannot get passwd entry. %s.\n", strerror(errno)); break;}
          if(!args[1] || !strcmp(args[1], "~"))
            {
             sprintf(placedir,"/home/%s", ourPWD->pw_name);
            }
          else
            {
             if(args[1][0] != '~') {sprintf(placedir, "%s", args[1]);}
             else
             {
               sprintf(placedir,"/home/%s", ourPWD->pw_name);
               if(chdir(placedir)) {fprintf(stderr, "Error: Cannot change directory to %s. %s.\n", placedir, strerror(errno));}
               sprintf(placedir,"%s", &args[1][2]);
             }
            }
          if(chdir(placedir)) {fprintf(stderr, "Error: Cannot change directory to %s. %s.\n", placedir, strerror(errno));}
          break;
        case(EXIT):
          if(fp) {fclose(fp); fp = NULL;}
          if(dr) {closedir(dr); dr = NULL;}
          if(curStat) {free(curStat); curStat = NULL;}
          return T_EXIT;
          break;
        case(PWD):
          if(!getcwd(cwd, PATH_MAX)) {fprintf(stderr, "Error: Cannot get current working directory. %s.\n", strerror(errno)); break;}
          printf("%s\n", cwd);
          break;
        case(LF):
          dr = opendir(".");
          if(!dr) {fprintf(stderr, "Error: Cannot open current directory. %s.\n", strerror(errno)); break;}
          while ((direntry = readdir(dr)) != NULL)
          {
            if(!strcmp(direntry->d_name, ".") || !strcmp(direntry->d_name, "..")) {continue;}
            printf("%s\n", direntry->d_name);
          }
          break;
        case(LP):
          dr = opendir("/proc");
          while ((direntry = readdir(dr)) != NULL)
          {
            if(strspn(direntry->d_name, "0123456789") != strlen(direntry->d_name)) {continue;}
            if(strlen(direntry->d_name) > maxLength)
            {
              maxLength = strlen(direntry->d_name);
            }
          }
          closedir(dr);
          dr = opendir("/proc");
          while ((direntry = readdir(dr)) != NULL)
          {
            if(strspn(direntry->d_name, "0123456789") != strlen(direntry->d_name)) {continue;}

            sprintf(placedir, "/proc/%s", direntry->d_name);
            if(!curStat) {fprintf(stderr, "Error: malloc() failed. %s.\n", strerror(errno)); return T_CONTINUE;}
            if(stat(placedir, curStat)) {fprintf(stderr, "Error: Cannot open stat of directory %s. %s.\n", placedir, strerror(errno)); continue;}

            ourPWD = getpwuid(curStat->st_uid);
            if(!ourPWD) {fprintf(stderr, "Error: Cannot get passwd entry. %s.\n", strerror(errno)); continue;}

            sprintf(placedir, "/proc/%s/cmdline", direntry->d_name);
            fp = fopen(placedir, "r");
            fgets(cmdline, sizeof(cmdline), fp);
            if(!strcmp(cmdline, "")) {continue;} //ignore zombies or fget errors, dosent print error

            printf("%*s %s %s\n", maxLength, direntry->d_name, ourPWD->pw_name, basename(cmdline));
            fclose(fp);
            fp = NULL;
          }
          break;
        case(EXEC):
          childPID = fork();
          if(childPID < 0) {fprintf(stderr, "Error: fork() failed. %s.\n", strerror(errno)); break;}
          if(childPID == 0)
          {
            if(execvp (args[0], args) < 0) {fprintf(stderr, "Error: exec() failed. %s.\n", strerror(errno));}
            exit(EXIT_FAILURE); // avoid copies on exec failure
          }
          if(waitpid(childPID, &status, 0) < 0 && (errno != EINTR)) {fprintf(stderr, "Error: wait() failed. %s.\n", strerror(errno)); break;}
          break;
        case(EMPTY):
          break;
    }
    if(fp) {fclose(fp); fp = NULL;}
    if(dr) {closedir(dr); dr = NULL;}
    if(curStat) {free(curStat); curStat = NULL;}
    return T_CONTINUE;
}

void printDir()
{
  char cwd[PATH_MAX];
  if(!getcwd(cwd, PATH_MAX)) {fprintf(stderr, "Error: Cannot get current working directory. %s.\n", strerror(errno)); return;}
  printf("%s[%s]%s>", BLUE, cwd, DEFAULT);
}

void splitArgs(char* args[], char inString[])
{
  memset(args, 0, PATH_MAX);
  char *token = strtok(inString, " ");
  int index = 0;
  while (token != NULL)
  {
    args[index++] = token;
    token = strtok(NULL, " ");
  }

  args[index] = NULL;
}

void sigHandle(int sig)
{
    interrupted = 1;
    fflush(stdout);
}

int main()
{
    char command[PATH_MAX];
    char *args[PATH_MAX];

    struct sigaction action = {0};
    action.sa_handler = sigHandle;
    sigemptyset(&action.sa_mask);
    action.sa_flags = 0;
    if(sigaction(SIGINT, &action, NULL)) {fprintf(stderr, "Error: Cannot register signal handler. %s.\n", strerror(errno)); return EXIT_FAILURE;}

    printDir();
    if(!fgets(command, PATH_MAX, stdin) && errno != EINTR) {fprintf(stderr, "Error: Failed to read from stdin. %s.\n", strerror(errno)); command[0] = '\0';}
    else {command[strcspn(command, "\n")] = '\0';} //we gotta get rid of \n because I used fgets
    splitArgs(args, command);

    while(interrupted || !runShellCMD(getCmd(args[0]), args))
    {
       if(interrupted) {printf("\n"); interrupted = 0;}
       printDir();
       if(!fgets(command, PATH_MAX, stdin) && errno != EINTR) {fprintf(stderr, "Error: Failed to read from stdin. %s.\n", strerror(errno)); command[0] = '\0';}
       else {command[strcspn(command, "\n")] = '\0';}
       splitArgs(args, command);
    }

    return EXIT_SUCCESS;
}