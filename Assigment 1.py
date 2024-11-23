import os
from openai import OpenAI

# Use the API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Example request to OpenAI
completion = client.chat.completions.create(
    model="gpt-4o-mini",  # Replace with the exact model name you are using
    messages=[
        {"role": "user", "content": "Create a Python program that checks if a number is prime."}
    ]
)

# Print the response
print(completion.choices[0].message.content)

#Extract the generated code from the response
generated_code = completion.choices[0].message.content

# Filter out non-code text (e.g., introductory explanations)
# This assumes the code is enclosed within triple backticks ```python
if "```python" in generated_code:
    generated_code = generated_code.split("```python")[1].split("```")[0].strip()
else:
    generated_code = generated_code.strip()  # Fallback: assume entire content is code
    
#Write the generated code to a file named "generatedcode.py"
file_name = "generatedcode.py"
with open(file_name,"w") as file:
    file.write(generated_code)
    
print(f"The generated code has been written to {file_name}.")    