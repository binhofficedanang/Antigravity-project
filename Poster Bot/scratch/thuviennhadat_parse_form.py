from bs4 import BeautifulSoup

def main():
    with open("thuviennhadat_dangtin.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, "html.parser")
    
    print("=== CÁC PHẦN TỬ TRÊN FORM ĐĂNG TIN ===")
    
    # 1. Các Nút Bán/Cho Thuê
    print("\n1. Nhu cầu:")
    demand_buttons = soup.select(".demand-button, [class*='demand']")
    for btn in demand_buttons:
        print(f"Text: '{btn.get_text().strip()}' | Class: '{btn.get('class')}' | Tag: {btn.name} | Attribute: {btn.attrs}")
        
    # 2. Các Dropdowns Địa chỉ
    print("\n2. Dropdowns Địa chỉ:")
    dropdowns = soup.select("select, .dropdown, [class*='dropdown']")
    for i, dd in enumerate(dropdowns):
        print(f"{i}. ID: '{dd.get('id')}' | Name: '{dd.get('name')}' | Class: '{dd.get('class')}' | Placeholder: '{dd.get('placeholder')}'")
        
    # 3. Các Inputs khác
    print("\n3. Inputs khác:")
    inputs = soup.select("input, textarea")
    for inp in inputs:
        print(f"ID: '{inp.get('id')}' | Name: '{inp.get('name')}' | Type: '{inp.get('type')}' | Placeholder: '{inp.get('placeholder')}'")

if __name__ == "__main__":
    main()
