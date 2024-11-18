import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to test OpenAI API


def test_openai_api():
    try:
        # Make a request to the OpenAI API to generate a response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Hello, OpenAI!"}
            ]
        )

        # Print the response from OpenAI
        print("OpenAI API Response:",
              response['choices'][0]['message']['content'])
    except Exception as e:
        print(f"Error occurred while calling OpenAI API: {e}")


# Run the test
if __name__ == "__main__":
    test_openai_api()
