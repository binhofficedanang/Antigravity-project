"""
Script đăng ký tài khoản tuần tự trên 6 trang BĐS
Chạy: ../venv/bin/python register_all.py
"""
import asyncio, time
from playwright.async_api import async_playwright

EMAIL    = "binh.officedanang@gmail.com"
PHONE    = "0935723727"
PASSWORD = "Binh1995@"
NAME     = "Binh Office Da Nang"

RESULTS  = {}

# ─────────────────────────────────────────
# 1. BDS123.VN
# form: fullname, phone, password, user_type (radio)
# ─────────────────────────────────────────
async def reg_bds123(page):
    print("\n=== [1/6] BDS123.VN ===")
    await page.goto("https://bds123.vn/dang-ky.html", wait_until="domcontentloaded", timeout=20000)
    await page.wait_for_timeout(2000)
    await page.fill('input[name="fullname"]', NAME)
    await page.fill('input[name="phone"]',    PHONE)
    await page.fill('input[name="password"]', PASSWORD)
    await page.locator('input[name="user_type"]').first.check()
    await page.screenshot(path="reg_bds123_form.png")
    await page.click('button[type="submit"], button:has-text("Đăng ký")')
    await page.wait_for_timeout(6000)
    await page.screenshot(path="reg_bds123_done.png")
    url = page.url
    print(f"  => URL: {url}")
    ok = "dang-nhap" in url or "tai-khoan" in url or "thanh-cong" in url or "xac-thuc" in url
    RESULTS["bds123.vn"] = "✅ OK" if ok else "🟡 Cần kiểm tra (xem reg_bds123_done.png)"
    print(f"  => {RESULTS['bds123.vn']}")

# ─────────────────────────────────────────
# 2. NHADATVN.COM.VN
# form tại / : sodienthoai, password
# ─────────────────────────────────────────
async def reg_nhadatvn(page):
    print("\n=== [2/6] NHADATVN.COM.VN ===")
    # Thử tìm link đăng ký trên homepage
    await page.goto("https://nhadatvn.com.vn/", wait_until="domcontentloaded", timeout=20000)
    await page.wait_for_timeout(2000)
    reg_links = await page.locator("a:has-text('Đăng ký'), a[href*='dang-ky']").all()
    if reg_links:
        href = await reg_links[0].get_attribute("href") or ""
        print(f"  => Link đăng ký: {href}")
        await page.goto(href if href.startswith("http") else "https://nhadatvn.com.vn" + href,
                        wait_until="domcontentloaded", timeout=15000)
    await page.wait_for_timeout(2000)
    await page.screenshot(path="reg_nhadatvn_form.png")

    # sodienthoai hoặc email
    for sel in ["input[name='sodienthoai']", "input[name='email']",
                "input[type='tel']", "input[type='email']",
                "input[placeholder*='điện thoại']", "input[placeholder*='Email']"]:
        try:
            if await page.locator(sel).count() > 0:
                await page.fill(sel, PHONE)
                break
        except: pass

    # password
    pw_fields = await page.locator("input[type='password']").all()
    for pw in pw_fields:
        try: await pw.fill(PASSWORD)
        except: pass

    # name nếu có
    for sel in ["input[name='hoten']", "input[name='name']",
                "input[placeholder*='họ tên']", "input[placeholder*='tên']"]:
        try:
            if await page.locator(sel).count() > 0:
                await page.fill(sel, NAME)
                break
        except: pass

    # submit
    for btn in ["button[type='submit']", "button:has-text('Đăng ký')",
                "input[type='submit']", "a:has-text('Đăng ký')"]:
        try:
            if await page.locator(btn).count() > 0:
                await page.click(btn)
                break
        except: pass

    await page.wait_for_timeout(6000)
    await page.screenshot(path="reg_nhadatvn_done.png")
    url = page.url
    print(f"  => URL: {url}")
    RESULTS["nhadatvn.com.vn"] = "🟡 Cần kiểm tra (xem reg_nhadatvn_done.png)"
    print(f"  => {RESULTS['nhadatvn.com.vn']}")

# ─────────────────────────────────────────
# 3. LUACHONNHADAT.VN
# dùng chung engine 123nhadatviet: femail, password
# ─────────────────────────────────────────
async def reg_luachon(page):
    print("\n=== [3/6] LUACHONNHADAT.VN ===")
    # Tìm trang đăng ký thực
    for url in [
        "https://luachonnhadat.vn/thanh-vien/dang-ky.html",
        "https://luachonnhadat.vn/dang-ky.html",
        "https://luachonnhadat.vn/",
    ]:
        try:
            r = await page.goto(url, wait_until="domcontentloaded", timeout=12000)
            if r and r.status == 200 and "dang-ky" in page.url:
                break
        except: pass

    await page.wait_for_timeout(2000)
    await page.screenshot(path="reg_luachon_form.png")

    # form 123nhadatviet engine: email, password
    for sel in ["input[name='femail']", "input[name='email']",
                "input[type='email']", "input[placeholder*='Email']",
                "input[placeholder*='email']"]:
        try:
            if await page.locator(sel).count() > 0:
                await page.fill(sel, EMAIL)
                break
        except: pass

    for sel in ["input[name='password']", "input[type='password']"]:
        try:
            if await page.locator(sel).count() > 0:
                await page.fill(sel, PASSWORD)
                break
        except: pass

    # họ tên nếu có
    for sel in ["input[name='display_name']", "input[name='hoten']",
                "input[placeholder*='tên']", "input[placeholder*='họ']"]:
        try:
            if await page.locator(sel).count() > 0:
                await page.fill(sel, NAME)
                break
        except: pass

    for btn in ["button[type='submit']", "input[type='submit']",
                "button:has-text('Đăng ký')", "span:has-text('Đăng ký')"]:
        try:
            if await page.locator(btn).count() > 0:
                await page.click(btn)
                break
        except: pass

    await page.wait_for_timeout(6000)
    await page.screenshot(path="reg_luachon_done.png")
    print(f"  => URL: {page.url}")
    RESULTS["luachonnhadat.vn"] = "🟡 Cần kiểm tra (xem reg_luachon_done.png)"
    print(f"  => {RESULTS['luachonnhadat.vn']}")

# ─────────────────────────────────────────
# 4. NHAONGAY.VN
# ─────────────────────────────────────────
async def reg_nhaongay(page):
    print("\n=== [4/6] NHAONGAY.VN ===")
    for url in [
        "https://nhaongay.vn/dang-ky",
        "https://nhaongay.vn/register",
        "https://nhaongay.vn/",
    ]:
        try:
            r = await page.goto(url, wait_until="domcontentloaded", timeout=12000)
            if r and r.status == 200:
                break
        except: pass

    await page.wait_for_timeout(2000)
    # Tìm link đăng ký
    for link_sel in ["a:has-text('Đăng ký')", "a[href*='register']", "a[href*='dang-ky']"]:
        try:
            links = await page.locator(link_sel).all()
            if links:
                href = await links[0].get_attribute("href") or ""
                if href:
                    await page.goto(href if href.startswith("http") else "https://nhaongay.vn" + href,
                                    wait_until="domcontentloaded", timeout=12000)
                    break
        except: pass

    await page.wait_for_timeout(2000)
    await page.screenshot(path="reg_nhaongay_form.png")

    # Fill form
    for sel in ["input[type='email']", "input[name='email']",
                "input[placeholder*='Email']", "input[placeholder*='email']"]:
        try:
            if await page.locator(sel).count() > 0:
                await page.fill(sel, EMAIL)
                break
        except: pass

    pw_fields = await page.locator("input[type='password']").all()
    for pw in pw_fields:
        try: await pw.fill(PASSWORD)
        except: pass

    for sel in ["input[name='name']", "input[name='fullname']",
                "input[placeholder*='tên']"]:
        try:
            if await page.locator(sel).count() > 0:
                await page.fill(sel, NAME)
                break
        except: pass

    for sel in ["input[name='phone']", "input[type='tel']",
                "input[placeholder*='điện thoại']"]:
        try:
            if await page.locator(sel).count() > 0:
                await page.fill(sel, PHONE)
                break
        except: pass

    for btn in ["button[type='submit']", "button:has-text('Đăng ký')",
                "input[type='submit']"]:
        try:
            if await page.locator(btn).count() > 0:
                await page.click(btn)
                break
        except: pass

    await page.wait_for_timeout(6000)
    await page.screenshot(path="reg_nhaongay_done.png")
    print(f"  => URL: {page.url}")
    RESULTS["nhaongay.vn"] = "🟡 Cần kiểm tra (xem reg_nhaongay_done.png)"
    print(f"  => {RESULTS['nhaongay.vn']}")

# ─────────────────────────────────────────
# 5. HOMEDY.COM
# ─────────────────────────────────────────
async def reg_homedy(page):
    print("\n=== [5/6] HOMEDY.COM ===")
    for url in [
        "https://homedy.com/Account/Register",
        "https://homedy.com/dang-ky-tai-khoan",
        "https://homedy.com/",
    ]:
        try:
            r = await page.goto(url, wait_until="domcontentloaded", timeout=12000)
            if r and r.status == 200 and "register" in page.url.lower() or "dang-ky" in page.url.lower():
                break
        except: pass

    await page.wait_for_timeout(2000)
    # Click link đăng ký nếu chưa vào trang
    for link_sel in ["a:has-text('Đăng ký')", "a[href*='Register']", "a[href*='register']"]:
        try:
            links = await page.locator(link_sel).all()
            if links:
                await links[0].click()
                await page.wait_for_timeout(2000)
                break
        except: pass

    await page.screenshot(path="reg_homedy_form.png")

    for sel in ["input[name='FullName']", "input[name='fullname']",
                "input[placeholder*='họ tên']", "input[placeholder*='Họ']"]:
        try:
            if await page.locator(sel).count() > 0:
                await page.fill(sel, NAME)
                break
        except: pass

    for sel in ["input[name='PhoneNumber']", "input[name='phone']",
                "input[type='tel']", "input[placeholder*='điện thoại']"]:
        try:
            if await page.locator(sel).count() > 0:
                await page.fill(sel, PHONE)
                break
        except: pass

    for sel in ["input[name='Email']", "input[name='email']",
                "input[type='email']"]:
        try:
            if await page.locator(sel).count() > 0:
                await page.fill(sel, EMAIL)
                break
        except: pass

    pw_fields = await page.locator("input[type='password']").all()
    for pw in pw_fields:
        try: await pw.fill(PASSWORD)
        except: pass

    for btn in ["button[type='submit']", "button:has-text('Đăng ký')",
                "input[type='submit']"]:
        try:
            if await page.locator(btn).count() > 0:
                await page.click(btn)
                break
        except: pass

    await page.wait_for_timeout(6000)
    await page.screenshot(path="reg_homedy_done.png")
    print(f"  => URL: {page.url}")
    RESULTS["homedy.com"] = "🟡 Cần kiểm tra (xem reg_homedy_done.png)"
    print(f"  => {RESULTS['homedy.com']}")

# ─────────────────────────────────────────
# 6. NHADAT.VN
# ─────────────────────────────────────────
async def reg_nhadat(page):
    print("\n=== [6/6] NHADAT.VN ===")
    for url in [
        "https://nhadat.vn/dang-ky",
        "https://nhadat.vn/register",
        "https://nhadat.vn/",
    ]:
        try:
            r = await page.goto(url, wait_until="domcontentloaded", timeout=12000)
            if r and r.status == 200:
                break
        except: pass

    await page.wait_for_timeout(2000)
    for link_sel in ["a:has-text('Đăng ký')", "a[href*='dang-ky']",
                     "a[href*='register']"]:
        try:
            links = await page.locator(link_sel).all()
            if links:
                href = await links[0].get_attribute("href") or ""
                if href:
                    await page.goto(href if href.startswith("http") else "https://nhadat.vn" + href,
                                    wait_until="domcontentloaded", timeout=12000)
                    break
        except: pass

    await page.wait_for_timeout(2000)
    await page.screenshot(path="reg_nhadat_form.png")

    for sel in ["input[type='email']", "input[name='email']",
                "input[placeholder*='Email']"]:
        try:
            if await page.locator(sel).count() > 0:
                await page.fill(sel, EMAIL)
                break
        except: pass

    for sel in ["input[type='tel']", "input[name='phone']",
                "input[placeholder*='điện thoại']"]:
        try:
            if await page.locator(sel).count() > 0:
                await page.fill(sel, PHONE)
                break
        except: pass

    pw_fields = await page.locator("input[type='password']").all()
    for pw in pw_fields:
        try: await pw.fill(PASSWORD)
        except: pass

    for btn in ["button[type='submit']", "button:has-text('Đăng ký')",
                "input[type='submit']"]:
        try:
            if await page.locator(btn).count() > 0:
                await page.click(btn)
                break
        except: pass

    await page.wait_for_timeout(6000)
    await page.screenshot(path="reg_nhadat_done.png")
    print(f"  => URL: {page.url}")
    RESULTS["nhadat.vn"] = "🟡 Cần kiểm tra (xem reg_nhadat_done.png)"
    print(f"  => {RESULTS['nhadat.vn']}")

# ─────────────────────────────────────────
# MAIN: chạy tuần tự 1 browser / 1 site
# ─────────────────────────────────────────
async def main():
    steps = [reg_bds123, reg_nhadatvn, reg_luachon,
             reg_nhaongay, reg_homedy, reg_nhadat]
    for fn in steps:
        async with async_playwright() as p:
            b = await p.chromium.launch(headless=False, slow_mo=700)
            ctx = await b.new_context(viewport={"width": 1280, "height": 800})
            page = await ctx.new_page()
            try:
                await fn(page)
            except Exception as e:
                name = fn.__name__.replace("reg_", "")
                print(f"  ❌ LỖI {name}: {e}")
                RESULTS[name] = f"❌ Lỗi: {str(e)[:60]}"
                await page.screenshot(path=f"reg_{name}_crash.png")
            finally:
                await b.close()
            await asyncio.sleep(2)

    print("\n\n" + "="*55)
    print("  KẾT QUẢ ĐĂNG KÝ")
    print("="*55)
    for site, res in RESULTS.items():
        print(f"  {site:25s} → {res}")

asyncio.run(main())
