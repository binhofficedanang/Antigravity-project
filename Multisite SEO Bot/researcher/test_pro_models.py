import os
import json
from google import genai

def test_models():
    api_key = "AIzaSyANZv0o0er5NM9nWQYpPJ6L9u-xWnapsJw"
    models_to_test = ["gemini-pro-latest", "gemini-2.5-pro", "gemini-2.0-flash"]
    
    client = genai.Client(api_key=api_key)
    for model_name in models_to_test:
        print(f"\n--- Testing model: {model_name} ---")
        try:
            response = client.models.generate_content(
                model=model_name,
                contents="Say 'Success' if you are working."
            )
            print(f"Result: {response.text.strip()}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_models()
