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
    
    # Query combotree roots
    ttp_nodes = bot.page.evaluate("""() => {
        try {
            const t = $('#cboTTP').combotree('tree');
            return t.tree('getRoots').map(n => ({ id: n.id, text: n.text }));
        } catch(e) {
            return e.message;
        }
    }""")
    print("cboTTP Tree Roots:", ttp_nodes)
    
    # Let's find Da Nang (usually id is starting with something or contains 'Đà Nẵng')
    da_nang_node = None
    if isinstance(ttp_nodes, list):
        for n in ttp_nodes:
            if 'đà nẵng' in n['text'].lower():
                da_nang_node = n
                print("Đà Nẵng Node Found:", n)
                break
                
    if da_nang_node:
        # Let's set it and get the children nodes for ward/district!
        children = bot.page.evaluate(f"""() => {{
            try {{
                const t = $('#cboTTP').combotree('tree');
                const node = t.tree('find', '{da_nang_node["id"]}');
                // Select/expand it to load children if ajax
                $('#cboTTP').combotree('setValue', '{da_nang_node["id"]}');
                return t.tree('getChildren', node.target).map(c => ({{ id: c.id, text: c.text }}));
            }} catch(e) {{
                return e.message;
            }}
        }}""")
        print("Đà Nẵng Wards/Districts:", children)
        
    nhom_nodes = bot.page.evaluate("""() => {
        try {
            // Is it a combotree or combobox? Let's check combobox first, then combotree
            if ($('#cboNhomNhaThue').hasClass('combotree-f')) {
                return $('#cboNhomNhaThue').combotree('tree').tree('getRoots').map(n => ({ id: n.id, text: n.text }));
            } else {
                return $('#cboNhomNhaThue').combobox('getData').map(n => ({ id: n.id, text: n.text }));
            }
        } catch(e) {
            return e.message;
        }
    }""")
    print("cboNhomNhaThue Nodes:", nhom_nodes)
    
finally:
    bot.stop()
