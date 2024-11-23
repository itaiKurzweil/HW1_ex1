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
