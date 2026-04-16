import os
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types


def main():
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt for Gemini")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "API key not found. Please set the GEMINI_API_KEY environment variable."
        )

    client = genai.Client(api_key=api_key)
    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

    generate_content(client, messages, args)


def generate_content(client, messages, args):
    response = client.models.generate_content(model="gemma-4-31b-it", contents=messages)

    if not response.usage_metadata:
        raise RuntimeError(
            "Failed API request. Usage metadata is missing from the response."
        )

    if args.verbose:
        print(f"User prompt: {messages[0].parts[0].text}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
        print(f"Response:\n{response.text}")

    print(response.text)


if __name__ == "__main__":
    main()
