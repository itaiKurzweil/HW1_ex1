import os
import subprocess
import random
from openai import OpenAI

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

def get_program_from_user():
    """Prompt the user for a program or return a random one from the list."""
    user_input = input(
        "I’m Super Python Coder. Tell me, which program would you like me to code for you? "
        "If you don't have an idea, just press Enter and I will choose a random program to code: "
    )
    if user_input.strip() == "":
        chosen_program = random.choice(PROGRAMS_LIST)
        print(f"Randomly chosen program: {chosen_program}")
        return chosen_program
    return user_input

def generate_program_with_openai(prompt, error_message=None):
    """Generate code using OpenAI's API based on the given prompt, optionally including error context."""
    messages = [
        {"role": "user", "content": f"{prompt}. Provide only the Python code as plain text, without any explanations, comments, or formatting markers."}
    ]
    if error_message:
        messages.append(
            {"role": "user", "content": f"The previous code had these errors: {error_message}. Please fix the code and provide the entire corrected version."}
        )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return response.choices[0].message.content.strip()

def run_generated_code(file_path, timeout=30):
    """Run the generated code with a timeout."""
    try:
        print("Running the generated code...")
        result = subprocess.run(
            ["python", file_path],
            text=True,
            capture_output=True,
            check=True,
            timeout=timeout,
            encoding="utf-8"
        )
        print("\nOutput from the generated code:")
        print(result.stdout)
        print("Code creation completed successfully!")
        return True, None  # Success
    except subprocess.TimeoutExpired:
        return False, "Execution timed out."
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def main():
    # Get the program idea from the user
    program_prompt = get_program_from_user()

    error_message = None
    max_retries = 5
    retry_count = 0

    while retry_count < max_retries:
        # Generate the code
        try:
            print(f"Attempt {retry_count + 1}: Generating code...")
            generated_code = generate_program_with_openai(program_prompt, error_message)
        except Exception as e:
            print(f"Error while generating code: {e}")
            break

        # Save the code to a file
        file_path = "generated_code.py"
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(generated_code)

        # Run the generated code
        success, error_message = run_generated_code(file_path, timeout=30)

        if success:
            print("Code executed successfully!")
            break  # Exit the loop on success
        else:
            print(f"Error running generated code! Error: {error_message}. Trying again...")
            retry_count += 1

    if retry_count == max_retries:
        print("Code generation FAILED")

if __name__ == "__main__":
    main()
