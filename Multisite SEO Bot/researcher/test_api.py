import os
import json
from google import genai

def test_gemini():
    api_key = "AIzaSyANZv0o0er5NM9nWQYpPJ6L9u-xWnapsJw"
    model_name = "gemini-1.5-pro" # Testing the "Pro" model
    
    print(f"Testing model: {model_name}")
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            contents="Say 'Hello' if you are working."
        )
        print("Response:", response.text)
    except Exception as e:
        print("Error encountered:")
        print(e)

if __name__ == "__main__":
    test_gemini()
