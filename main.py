import os
import sys
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types
from config import MAX_ITERS
from prompts import system_prompt
from call_function import available_functions, call_function

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

    if args.verbose:
        print(f"User prompt: {args.user_prompt}\n")

    for _ in range(MAX_ITERS):
        try:
            final_reponse = generate_content(client, messages, args.verbose)
            if final_reponse:
                print("Final Response: ")
                print(final_reponse)
                return
        except Exception as e:
            print(f"Error in generate_content: {e}")

    print(f"Maximum iterations ({MAX_ITERS}) reached without a final response.")
    sys.exit(1)


def generate_content(client, messages, verbose):
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        ),
    )

    if response.candidates:
        for candidate in response.candidates:
            messages.append(candidate.content)

    if not response.usage_metadata:
        raise RuntimeError(
            "Failed API request. Usage metadata is missing from the response."
        )

    if verbose:
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    if response.candidates:
        for candidate in response.candidates:
            if candidate.content:
                messages.append(candidate.content)

    if not response.function_calls:
        return response.text

    function_responses = []
    for function_call in response.function_calls:
        result = call_function(function_call, verbose)
        if (
            not result.parts
            or not result.parts[0].function_response
            or not result.parts[0].function_response.response
        ):
            raise RuntimeError(f"Empty function response for {function_call.name}")

        if verbose:
            print(f"-> {result.parts[0].function_response.response}")

        function_responses.append(result.parts[0])

    messages.append(types.Content(role="user", parts=function_responses))

if __name__ == "__main__":
    main()
