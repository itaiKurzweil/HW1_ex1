import os
import subprocess
import random
from tqdm import tqdm  # For progress bar
from openai import OpenAI
from colorama import Fore, Style, init
import time
import re

# Initialize colorama
init(autoreset=True)
max_attempts = 5
# Set your OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)  # Instantiate the OpenAI client

# Hardcoded list of programs
PROGRAMS_LIST = [
    '''"Given two strings str1 and str2, prints all interleavings of the given
        two strings. You may assume that all characters in both strings are
        different.Input: str1 = "AB", str2 = "CD"
        Output:
            ABCD
            ACBD
            ACDB
            CABD
            CADB
            CDAB
        Input: str1 = "AB", str2 = "C"
        Output:
        ABC
        ACB
        CAB "''',
    "Write a Python program to check if a number is a palindrome.",
    "Write a Python program to find the kth smallest element in a given binary search tree.",
    "Write a Python program to detect if a linked list has a cycle. Use Floyd's cycle-finding algorithm (tortoise and hare approach).",
    "Write a Python program to solve the N-Queens problem using backtracking and print all possible solutions for a given board size N."
]

def auto_fix_code(code):
    """Automatically fix simple lint issues in the code."""
    # Remove trailing whitespace
    fixed_code = "\n".join(line.rstrip() for line in code.splitlines())
    
    # Ensure the file ends with exactly one newline
    if not fixed_code.endswith("\n"):
        fixed_code += "\n"

    # Add a module-level docstring if missing
    if not fixed_code.lstrip().startswith('"""'):
        docstring = '"""\nThis module provides functionality for the requested program.\n"""\n\n'
        fixed_code = docstring + fixed_code

    # Add missing docstrings for functions and classes
    lines = fixed_code.splitlines()
    updated_lines = []
    for line in lines:
        if line.strip().startswith("def ") and '"""' not in line:
            updated_lines.append('    """Placeholder docstring."""')
        if line.strip().startswith("class ") and '"""' not in line:
            updated_lines.append('    """Placeholder class docstring."""')
        updated_lines.append(line)
    fixed_code = "\n".join(updated_lines)

    return fixed_code

def run_lint_check():
    """Run pylint on the given file and return the output."""
    result = subprocess.run(['pylint', "generatedcode.py"], capture_output=True, text=True)
    return result.stdout  # Return lint output and success status

def generate_program_with_openai_for_lint(code, max_attempts=3):
    """
    Generate code using OpenAI's API to resolve lint issues iteratively.

    Args:
        code (str): The original program code.
        max_attempts (int): Maximum number of attempts to resolve lint issues.

    Returns:
        str: The final generated code after resolving lint issues.
    """
    lint_issues = ""  # Initialize lint issues as an empty string

    for attempt in tqdm(range(1, max_attempts + 1), desc="Resolving lint issues"):

        # Prepare the messages for OpenAI API
        messages = [
            {
                "role": "user",
                "content": (
                    f"""Fix the following Python code to resolve these pylint errors/warnings:
                    Code:\n{code}\n\n
                    Pylint Errors/Warnings:\n{lint_issues} just write code, no extra information and words
                    Ensure the output is fully executable as-is in a Python environment. 
                    Go line by line and check if the response is runnable in Python, paying attention to the first and last lines to avoid extra syntax.
                    Make sure!!!!!!! about the last command I gave you!!!!!!!! Make it runnable with no changes at all!!!! 
                    Delete the ```python on the first line and the closing ``` on the last line.
                    no matter what you do, do not give output before making sure this happens!!!!!!!!!!!!! .
                    write the code as plain text without code block"""
                ),
            },
        ]

        try:
            # Call OpenAI to generate updated code
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            code = response.choices[0].message.content.strip("```python\n").strip("```") + "\n"
            lint_output = run_lint_check()
       
            if "10.00/10" in lint_output:
                print(f"Lint issues resolved on attempt {attempt}.")
                continue
            else:
                lint_issues = lint_output
        except Exception as e:
                print(f"Error during attempt {attempt}: {e}")
        else:
            with open("generatedcode.py", "w", encoding="utf-8") as file:
                file.write(code)
    

    print(Fore.RED + "Reached the maximum number of attempts. Returning the best effort.")
    return code


def generate_program_with_openai(user_input):
    """Generate code using OpenAI's API based on the given user input."""
    errs = ""
    prompt = f"""Write a Python program that performs the following: {user_input}
    Provide only the runnable Python code and corresponding unit tests as plain text, without any explanations, comments, or additional formatting.
    Ensure the code includes edge cases in the tests and produces the correct output for all cases.
    Do not include any text other than the code and the tests.
    after writing the code, check line by line and erase the '''python prefix and ''' suffix from the code. make it runable python code.!!!!!!!
    Go line by line and check if the response is runnable in Python, paying attention to the first and last lines to avoid extra syntax.
    make sure!!!!!!! about the last command i gave you!!!!!!!! make it run able with no chages at all!!!!
    Delete the ```python\ on the first line and the closing ``` on the\u00a0last\u00a0line.
    Delete this ```python and this ```
    write the code as plain text without code block"""
    messages = [
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
        )
    
    generated_code = response.choices[0].message.content.strip("```python\n").strip("```")+ "\n"
    with open("generatedcode.py", "w") as file:
        file.write(generated_code)
        

    try:
        subprocess.run(["python","generatedcode.py"], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        errs = e.stderr
        print(Fore.RED + f"Error running generated code! Eror:{errs}. Trying again.") 
        for i in tqdm(range (1,max_attempts-1), desc="Retrying code generation"):
            prompt = (
                "Write a Python program that does the following:\n" 
                + user_input + "\n"
                "Notice the previous code failed some tests. Please fix the code and try again. "
                "Keep the same tests!!!!! Do not change it!!!! Only fix the code!\n"
                + generated_code + "\n"
                "These are the erors:\n" + errs + "\n"
                "Provide only the Python code as plain text, without any explanations, comments, or formatting markers.\n"
                "Do not include any text other than the code and the tests.\n"
                "After writing the code, check line by line and erase any ```python prefix and ``` suffix from the code. "
                "Make it runnable Python code!!!!!!!!!!!!!! do it!!!!.\n"
                "Delete this ```python and this ```!!!!!!! do not give ouptut before making sure this happens!!!!!!!!!!!!! .\n"
                "write the code as plain text without code block"
)

            messages = [
            {"role": "user", "content": prompt}
            ]
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            generated_code = response.choices[0].message.content.strip("```python\n").strip("```") + "\n"
            with open("generatedcode.py", "w") as file:
                file.write(generated_code)
            try:
                subprocess.run(["python","generatedcode.py"], capture_output=True, text=True, check=True)
            except subprocess.CalledProcessError as error:
                errs = error.stderr
                print(Fore.RED + f"Error running generated code! Eror:{errs}. Trying again.")
                continue
            else:
                print(Fore.GREEN + "All tests passed successfully")
                return generated_code, True 
        return generated_code, False
    else:
        print(Fore.GREEN + "All tests passed successfully")
        return generated_code, True


def optimized_code_with_openai(generated_code):
    """Optimize code using OpenAI's API based on the given code."""
    prompt = (
        "According to the instructionsn improve the code if possible. \n"
        "The instruction is:\n"
        "If you can't, write the same code again. Include the unit tests as well, make sure it's exactly the same tests as before.\n"
        "No extra information, just the code and tests! "
        "Ensure the output is fully executable as-is in a Python environment. "
        "Go line by line and check if the response is runnable in Python, paying attention to the first and last lines to avoid extra syntax.\n"
        'Delete the """python" from all.\n'
        "write the code as plain text without code block.\n"
        "The code is:\n"
        + generated_code 
        + "\n"
    )

    messages = [
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    optimized_code = response.choices[0].message.content.strip("```python\n").strip("```") + "\n"

    # Measure the execution time of the original code
    start_time = time.time()
    subprocess.run(["python","generatedcode.py"], capture_output=True, text=True, check=True)
    end_time = time.time()
    old_code_time = end_time - start_time
    
    # Save the optimized code to a file
    with open("generatedcode.py", "w", encoding="utf-8") as file:
        file.write(optimized_code)
    try:
        start_time = time.time()
        subprocess.run(["python", "generatedcode.py"], capture_output=True, text=True, check=True)
        end_time = time.time()
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"Error running optimized code! Error: {e.stderr}")
        with open("generatedcode.py", "w", encoding="utf-8") as file:
            file.write(generated_code)
        return generated_code
    else:
        new_code_time = end_time - start_time
        if new_code_time < old_code_time:
            print(Fore.GREEN + "Optimized code is faster than the original code")
            return optimized_code
        else:
            print(Fore.RED + "Optimized code is slower than the original code")
            with open("generatedcode.py", "w", encoding="utf-8") as file:
                file.write(generated_code)
            return generated_code


def get_program_from_user():
    """Prompt the user for a program or return a random one from the list."""
    user_input = input(
        Fore.BLUE + Style.BRIGHT +
        "I’m Super Python Coder. Tell me, which program would you like me to code for you?\n"
        "If you don't have an idea, just press Enter and I will choose a random program to code:\n"
    )
    if user_input.strip() == "":
        chosen_program = random.choice(PROGRAMS_LIST)
        print(Fore.CYAN + f"Randomly chosen program: {chosen_program}")
        return chosen_program
    return user_input


def main():
    print(Fore.GREEN + Style.BRIGHT + "Welcome to Super Python Coder!")
    program_prompt = get_program_from_user()

    # First pass: Generate initial code
    print(Fore.CYAN + f"Generating initial code for: {program_prompt}")
    generated_code, status = generate_program_with_openai(program_prompt)
    if not status:
        print(Fore.RED + "Failed to generate code that passes the tests.")
        return
    optimized_code = optimized_code_with_openai(generated_code)

    optimized_code = generate_program_with_openai_for_lint(optimized_code)

if __name__ == "__main__":
    main()
