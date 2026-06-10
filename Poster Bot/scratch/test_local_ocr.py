import easyocr
import sys
import os

def test():
    if not os.path.exists("sample_captcha.png"):
        print("sample_captcha.png not found")
        sys.exit(1)
        
    print("Initializing EasyOCR reader...")
    reader = easyocr.Reader(['en'])
    print("Reading sample_captcha.png...")
    result = reader.readtext('sample_captcha.png')
    print("Result:")
    for res in result:
        text = res[1]
        digits = "".join(c for c in text if c.isdigit())
        print(f"Detected text: '{text}', digits: '{digits}'")

if __name__ == '__main__':
    test()
