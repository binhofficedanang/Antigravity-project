import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from web_automation import WebAutomation

bot = WebAutomation(headless=False)
try:
    bot.start()
    bot.login_dangtinbatdongsan("binhofficedanang", "Binh1995@")
    time.sleep(3)
    
    bot.page.goto("https://dangtinbatdongsan.vn/qttv/nhathue", wait_until="domcontentloaded")
    time.sleep(3)
    bot.page.click("#btnThem")
    time.sleep(2)
    
    # 1. Set TTP value to '48' (Đà Nẵng)
    bot.page.evaluate("$('#cboTTP').combotree('setValue', '48')")
    print("Set cboTTP to 48 (Đà Nẵng). Waiting 3 seconds for cboXa to load...")
    time.sleep(3)
    
    # 2. Query cboXa tree roots/children
    xa_nodes = bot.page.evaluate("""() => {
        try {
            const t = $('#cboXa').combotree('tree');
            return t.tree('getRoots').map(n => ({
                id: n.id,
                text: n.text,
                // Get immediate children if loaded
                children: t.tree('getChildren', n.target).slice(0, 5).map(c => ({ id: c.id, text: c.text }))
            }));
        } catch(e) {
            return e.message;
        }
    }""")
    
    print("cboXa Nodes:")
    for n in xa_nodes:
        print(f"  Root: id={n['id']}, text={n['text']}")
        if n.get('children'):
            print(f"    Children preview: {n['children']}")
            
finally:
    bot.stop()
