import os
import subprocess
import random
from tqdm import tqdm  # For progress bar
from openai import OpenAI
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

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

def run_lint_check(file_path):
    """Run pylint on the given file and return the output."""
    try:
        result = subprocess.run(
            ["pylint", file_path],
            text=True,
            capture_output=True,
            check=False
        )
        return result.stdout, result.returncode == 0  # Return lint output and success status
    except FileNotFoundError:
        print(Fore.RED + "Pylint is not installed or not found. Please ensure it is installed.")
        exit(1)

def generate_program_with_openai(prompt, lint_issues=None):
    """Generate code using OpenAI's API based on the given prompt."""
    messages = [
        {"role": "user", "content": f"{prompt}. Provide only the Python code as plain text, without any explanations, comments, or formatting markers."}
    ]
    if lint_issues:
        messages.append(
            {
                "role": "user",
                "content": (
                    f"The following lint issues were found in the previous code:\n{lint_issues}\n"
                    "Please fix these issues to achieve a Pylint rating of 10/10. Specifically:\n"
                    "- Ensure the file ends with exactly one newline (C0304).\n"
                    "- Add a module-level docstring at the top of the file describing the purpose of the code (C0114). For example:\n"
                    "\"\"\"\n"
                    "This module provides functionality for solving the requested problem.\n"
                    "It includes detailed explanations and examples of use.\n"
                    "\"\"\"\n"
                    "- Add meaningful docstrings for all functions and methods (C0116).\n"
                    "- Add meaningful docstrings for all classes (C0115).\n"
                    "- Rename constants to follow PEP8 naming conventions. Use `UPPER_CASE` for constants and descriptive names (C0103).\n"
                    "- Retain the functionality of the code while addressing these issues and ensure the output passes Pylint checks with a score of 10/10."
                )
            }
        )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return response.choices[0].message.content.strip()

def lint_and_fix(file_path, program_prompt, retries=3):
    """Run lint checks and use OpenAI API to fix issues."""
    with tqdm(total=retries, desc=Fore.YELLOW + "Fixing Lint Issues", ncols=80) as progress_bar:
        for attempt in range(retries):
            # Run pylint to check the file
            lint_output, lint_success = run_lint_check(file_path)
            if lint_success:
                print(Fore.GREEN + "Amazing. No lint errors/warnings.")
                return True

            print(Fore.RED + f"Lint issues found:\n{lint_output}")
            print(Fore.YELLOW + f"Attempting to fix lint issues (attempt {attempt + 1}/{retries})...")

            # Read the current code
            with open(file_path, "r", encoding="utf-8") as file:
                code = file.read()

            # Apply automatic fixes for trivial issues
            code = auto_fix_code(code)

            # Save the auto-fixed code back to the file
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(code)

            # Use OpenAI API to address deeper issues
            fixed_code = generate_program_with_openai(
                program_prompt,
                lint_issues=lint_output
            )

            # Save the AI-fixed code back to the file
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(fixed_code)

            # Update progress bar
            progress_bar.update(1)

    # If we exhaust retries, log remaining issues for manual review
    print(Fore.RED + "\nUnable to pass lint checks after multiple attempts. Remaining issues:")
    print(lint_output)
    with open("unresolved_lint_issues.log", "w", encoding="utf-8") as log_file:
        log_file.write(lint_output)
    print(Fore.YELLOW + "Remaining issues logged in 'unresolved_lint_issues.log'. Please review manually.")
    return False

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
    generated_code = generate_program_with_openai(program_prompt)

    # Save the generated code to a file
    file_path = "generated_code.py"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(generated_code)

    # Second pass: Run lint checks and fix issues
    print(Fore.CYAN + "\nRunning lint checks and attempting fixes...")
    lint_success = lint_and_fix(file_path, program_prompt)

    if lint_success:
        print(Fore.GREEN + "\nAmazing. No lint errors/warnings!")
    else:
        print(Fore.RED + "\nThere are still lint errors/warnings.")
        exit(1)

if __name__ == "__main__":
    main()
