import os
from openai import OpenAI  
import subprocess
import random

# Set your OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)  # Instantiate the OpenAI client

# Hardcoded list of programs
PROGRAMS_LIST = [
    "Write a Python program to check if a number is a palindrome.",
    "Write a Python program to find the kth smallest element in a given binary search tree."
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

def generate_program_with_openai(prompt):
    """Generate code using OpenAI's API based on the given prompt."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": f"{prompt}.Provide only the Python code as plain text, without any explanations, comments, or formatting markers."
            }
        ]
    )
    return response.choices[0].message.content.strip()

def main():
    # Get the program idea from the user
    program_prompt = get_program_from_user()

    # Generate the code
    try:
        print("Generating code...")
        generated_code = generate_program_with_openai(program_prompt)
    except Exception as e:
        print(f"Error while generating code: {e}")
        return

    # Save the code to a file
    file_path = "generated_code.py"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(generated_code)

    # Run the generated code
    try:
        print("Running the generated code...")
        result = subprocess.run(["python", file_path], text=True, capture_output=True, check=True, encoding="utf-8")
        print("\nOutput from the generated code:")
        print(result.stdout)
        print("Code creation completed successfully!")
    except subprocess.CalledProcessError as e:
        print("\nAn error occurred while running the generated code:")
        print(e.stderr)
        return

    # Open the file in the default text editor
    print("Opening the generated code...")
    subprocess.call(["start", file_path], shell=True)

if __name__ == "__main__":
    main()

