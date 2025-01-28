"""
NameError: name 'variable_name' is not defined

This error occurs when you try to access a variable or function that has not been defined in the code. 
It is often caused by typos or forgetting to declare the variable before using it.
"""

#--------------------------

"""
Video Script:

1. Start by saying: "Hey everyone! Today, we're diving into a common Python error: the NameError."
2. Explain briefly: "The NameError usually happens when you try to use a variable or function that doesn't exist yet. It's often caused by a simple typo or missing declaration."
3. Demonstrate with an example: "Let's see this in action. Here's a piece of code that will trigger the error."
4. Show the error in your editor or terminal and then say: "Oops! See? Python's telling us the variable isn't defined."
"""

#--------------------------


# Code that triggers the NameError
print(my_variable)  # This will trigger a NameError because 'my_variable' is not defined


#--------------------------

"""
Traceback (most recent call last):
  File "/workspaces/disent/name_error.py", line 18, in <module>
    print(my_variable)  # This will trigger a NameError because 'my_variable' is not defined
          ^^^^^^^^^^^
NameError: name 'my_variable' is not defined
"""

