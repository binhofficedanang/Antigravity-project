import os
from google import genai

def list_models():
    api_key = "AIzaSyANZv0o0er5NM9nWQYpPJ6L9u-xWnapsJw"
    try:
        client = genai.Client(api_key=api_key)
        print("Available models:")
        for model in client.models.list():
            print(f"- {model.name}")
    except Exception as e:
        print("Error listing models:")
        print(e)

if __name__ == "__main__":
    list_models()
