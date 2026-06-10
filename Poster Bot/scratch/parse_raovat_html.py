from bs4 import BeautifulSoup

def parse():
    with open("raovat_step1_after_click.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, "html.parser")
    # remove scripts and styles
    for s in soup(["script", "style"]):
        s.decompose()
        
    text = soup.get_text()
    # clean up whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = "\n".join(chunk for chunk in chunks if chunk)
    
    print("=== HTML TEXT ===")
    print(text[:2000])

if __name__ == "__main__":
    parse()
