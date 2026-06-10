import requests
import base64
import os
import time

def test_ocr():
    # Let's download a sample captcha from 123nhadatviet.com
    # Captcha URL: http://123nhadatviet.com/CaptchaGenerator.ashx?t=test
    print("Downloading sample captcha...")
    try:
        r = requests.get("http://123nhadatviet.com/CaptchaGenerator.ashx?t=test", timeout=10)
        img_bytes = r.content
        with open("sample_captcha.png", "wb") as f:
            f.write(img_bytes)
        print("Sample captcha saved to sample_captcha.png")
        
        # Convert to base64
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")
        
        # Send to ocr.space
        url = "https://api.ocr.space/parse/image"
        payload = {
            "apikey": "helloworld",
            "base64Image": f"data:image/png;base64,{img_base64}",
            "language": "eng",
            "isOverlayRequired": False,
            "OCREngine": 2 # Engine 2 is better for numbers/simple digits
        }
        print("Sending to ocr.space API...")
        res = requests.post(url, data=payload, timeout=15).json()
        print("API Response:")
        import pprint
        pprint.pprint(res)
        
        # Extract numbers
        parsed_results = res.get("ParsedResults", [])
        if parsed_results:
            text = parsed_results[0].get("ParsedText", "").strip()
            print(f"Parsed Text: '{text}'")
            # Extract digits only
            digits = "".join(c for c in text if c.isdigit())
            print(f"Extracted Digits: '{digits}'")
        else:
            print("No text parsed.")
            
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_ocr()
