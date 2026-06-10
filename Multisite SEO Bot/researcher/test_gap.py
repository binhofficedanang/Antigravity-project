import trafilatura
import sys
import os

def test_fetch():
    url = "https://officedanang.vn/cho-thue-van-phong-da-nang/"
    print(f"Testing fetch from: {url}")
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        content = trafilatura.extract(downloaded)
        if content:
            print("✅ Successfully extracted content!")
            print(f"Content preview (first 200 chars): {content[:200]}...")
        else:
            print("❌ Extracted content is empty.")
    else:
        print("❌ Failed to download URL.")

if __name__ == "__main__":
    test_fetch()
