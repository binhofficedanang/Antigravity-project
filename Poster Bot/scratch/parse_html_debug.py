import os
from html.parser import HTMLParser

class SimpleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current_tag = None
        self.forms = []
        self.current_form = None
        self.inputs = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        self.current_tag = tag
        
        if tag == "form":
            self.current_form = {
                "action": attrs_dict.get("action", ""),
                "id": attrs_dict.get("id", ""),
                "class": attrs_dict.get("class", ""),
                "method": attrs_dict.get("method", ""),
                "inputs": []
            }
            self.forms.append(self.current_form)
            
        elif tag in ["input", "button", "select", "textarea"]:
            inp = {
                "tag": tag,
                "name": attrs_dict.get("name", ""),
                "id": attrs_dict.get("id", ""),
                "type": attrs_dict.get("type", ""),
                "placeholder": attrs_dict.get("placeholder", ""),
                "class": attrs_dict.get("class", ""),
                "value": attrs_dict.get("value", "")
            }
            if self.current_form:
                self.current_form["inputs"].append(inp)
            else:
                self.inputs.append(inp)
                
        elif tag == "a":
            self.links.append({
                "href": attrs_dict.get("href", ""),
                "class": attrs_dict.get("class", ""),
                "id": attrs_dict.get("id", ""),
                "text": ""
            })

    def handle_endtag(self, tag):
        if tag == "form":
            self.current_form = None

    def handle_data(self, data):
        if self.current_tag == "a" and self.links:
            self.links[-1]["text"] += data.strip()

def analyze_file(filename):
    print(f"\n==========================================")
    print(f"ANALYZING: {filename}")
    print(f"==========================================")
    if not os.path.exists(filename):
        print(f"File {filename} does not exist.")
        return
        
    with open(filename, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
    parser = SimpleParser()
    parser.feed(content)
    
    print(f"Forms found: {len(parser.forms)}")
    for i, form in enumerate(parser.forms):
        print(f"  Form [{i}]: id='{form['id']}', class='{form['class']}', action='{form['action']}', method='{form['method']}'")
        for inp in form["inputs"]:
            print(f"    <{inp['tag']}> name='{inp['name']}', id='{inp['id']}', type='{inp['type']}', placeholder='{inp['placeholder']}', class='{inp['class']}', val='{inp['value']}'")
            
    print(f"Non-form inputs found: {len(parser.inputs)}")
    for inp in parser.inputs[:15]:
        print(f"  <{inp['tag']}> name='{inp['name']}', id='{inp['id']}', type='{inp['type']}', placeholder='{inp['placeholder']}', class='{inp['class']}', val='{inp['value']}'")
        
    print(f"Interesting links found: (total {len(parser.links)})")
    interesting_count = 0
    for link in parser.links:
        href = link["href"]
        text = link["text"].strip()
        if any(w in text.lower() or w in href.lower() for w in ["nhap", "login", "dang-ky", "register", "post", "dang-tin"]):
            print(f"  Link: '{text}' -> '{href}' (class='{link['class']}', id='{link['id']}')")
            interesting_count += 1
            if interesting_count >= 30:
                print("  ... truncated links list ...")
                break

def main():
    files = ["chonhadat_login.html", "nhaongay_login_modal.html", "nhadat_home.html", "nhadatvn_login.html"]
    for f in files:
        analyze_file(f)

if __name__ == "__main__":
    main()
