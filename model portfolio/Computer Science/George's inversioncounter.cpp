/*******************************************************************************
 * Name        : inversioncounter.cpp
 * Author      : George Oliynyk
 * Version     : 1.0
 * Date        : 11/2/2024
 * Description : Counts the number of inversions in an array.
 * Pledge      : I pledge my honor that I have abided by the Stevens Honor System
 ******************************************************************************/
#include <iostream>
#include <algorithm>
#include <sstream>
#include <vector>
#include <array>
#include <cstdio>
#include <cctype>
#include <cstring>

using namespace std;

// Function prototype.
static long mergesort(int array[], int scratch[], int low, int high);

/**
 * Counts the number of inversions in an array in Theta(n^2) time using two nested loops.
 */
long count_inversions_slow(int array[], int length) {
    //Initilize inversions counter
    long inversionsCounter = 0;
    //Outer loop for each value in arr
    for(int outerIndex = 0; outerIndex < length; outerIndex++)
    {
        //Inner loop for each value after current value in arr
        for(int innerIndex = outerIndex + 1; innerIndex < length; innerIndex++)
        {
            //if current value is more than value at InnerIndex, increase inversions
            if(array[outerIndex] > array[innerIndex])
            {
                inversionsCounter++;
            }
        }
    }
    return inversionsCounter;
}

/**
 * Counts the number of inversions in an array in Theta(n lg n) time.
 */
long count_inversions_fast(int array[],int length) {
    // TODO
    // Hint: Use mergesort!
    //dynamically allocate array for scratch work
    int* scratchArr = new int[length];
    //run mergesort to get inversions
    long inversions = mergesort(array, scratchArr, 0, length - 1);
    //deallocate array
    delete [] scratchArr;
    return inversions;
}


long merge(int A[], int B[], int lo, int mid, int hi)
{
    //Initial values initilization
    int i = lo;
    int i1 = lo;
    int i2 = mid+1;
    long inversions = 0;

    //loop to merge initial values based on comparison
    while(i1<=mid && i2<=hi)
    {
        if(A[i1]<=A[i2])
        {
            B[i++]=A[i1++];
        }
        else
        {
            B[i++] = A[i2++];
            //increment inversions when neccesary
            inversions += (mid - i1 + 1);
        }
    }

    //merge remaining values
    while(i1 <= mid)
    {
        B[i++] = A[i1++];
    }
    while(i2 <= hi)
    {
        B[i++] = A[i2++];
    }

    //copy arr B to arr A
    copy(B, B + hi + 1, A);
    return inversions;
}

static long mergesort(int array[], int scratch[], int low, int high) {
    //Recursive base case
    if(low >= high)
    {
        return 0;
    }
    //mergesort array in half
    int mid = low + (high - low)/2;
    long count = mergesort(array, scratch, low, mid);
    count += mergesort(array, scratch, mid+1, high);
    //run merge on current arrays
    count += merge(array, scratch, low, mid, high);
    return count;
}

int main(int argc, char *argv[]) {
    // TODO: parse command-line argument
    if(argc > 2)
    {
        cerr << "Usage: ./inversioncounter [slow]" << endl;
        return 1;
    }
    if(argc == 2 && string(argv[1]) != "slow")
    {
        cerr << "Error: Unrecognized option '" << argv[1] << "'." << endl;
        return 1;
    }

    cout << "Enter sequence of integers, each followed by a space: " << flush;

    istringstream iss;
    int value, index = 0;
    vector<int> values;
    string str;
    str.reserve(11);
    char c;
    while (true) {
        c = getchar();
        const bool eoln = c == '\r' || c == '\n';
        if (isspace(c) || eoln) {
            if (str.length() > 0) {
                iss.str(str);
                if (iss >> value) {
                    values.push_back(value);
                } else {
                    cerr << "Error: Non-integer value '" << str
                         << "' received at index " << index << "." << endl;
                    return 1;
                }
                iss.clear();
                ++index;
            }
            if (eoln) {
                if(values.size() <= 0)
                {
                    cerr << "Error: Sequence of integers not received." << endl;
                    return 1;
                }
                break;
            }
            str.clear();
        } else {
            str += c;
        }
    }

    // TODO: produce output
    cout << "Number of inversions" << (argc == 2 ? " (slow): " : " (fast): ") << (argc == 2 ? count_inversions_slow(values.data(), values.size()) : count_inversions_fast(values.data(), values.size())) << endl;

    return 0;
}
