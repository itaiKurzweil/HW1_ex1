import os
from openai import OpenAI
import subprocess

# Use the API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Example request to OpenAI
completion = client.chat.completions.create(
    model="gpt-4o-mini",  # Replace with the exact model name you are using
messages=[
    {"role": "user","content":"Write a Python program that checks if a number is prime. Include at least 10 unit tests with asserts to check the logic of the program and edge cases. Provide only the Python code as plain text, without any explanations, comments, or formatting markers."

    }
]

)

# Print the response
print(completion.choices[0].message.content)

#Extract the generated code from the response
generated_code = completion.choices[0].message.content


generated_code = generated_code.strip()  # Fallback: assume entire content is code
    
#Write the generated code to a file named "generatedcode.py"
file_name = "generatedcode.py"
with open(file_name,"w") as file:
    file.write(generated_code)

print(f"The generated code has been written to {file_name}.")


# Run the generatedcode.py file using subprocess.run
try:
    print("\nRunning the generated code...")
    result = subprocess.run(["python", file_name], text=True, capture_output=True, check=True)

    # Print the output of the script
    print("Output from generatedcode.py:")
    print(result.stdout)
except subprocess.CalledProcessError as e:
    # Handle errors that occur during the execution of generatedcode.py
    print("An error occurred while running the generated code:")
    print(e.stderr)    