import asyncio
import os
import sys
import time
from playwright.async_api import async_playwright

EMAIL = "binh.officedanang@gmail.com"
PHONE = "0935723727"
PASSWORD = "Binh1995@"
USERNAME = "binhofficedanang"

SITES = [
    {
        "name": "chonhadat24h.com",
        "url": "https://chonhadat24h.com/dang-nhap",
        "selectors": ["#email-login", "input[name='email']", "input[type='email']", "input[type='text']"]
    },
    {
        "name": "nhaongay.vn",
        "url": "https://nhaongay.vn/dang-nhap",
        "selectors": ["input[name='username']", "input[name='email']", "input[type='email']", "input[type='text']"]
    },
    {
        "name": "nhadat.vn",
        "url": "https://nhadat.vn/dang-nhap",
        "selectors": ["input[name='email']", "input[type='email']", "input[type='text']"]
    },
    {
        "name": "nhadatvn.com.vn",
        "url": "https://nhadatvn.com.vn/dang-nhap",
        "selectors": ["input[name='email']", "input[name='sodienthoai']", "input[type='text']"]
    },
    {
        "name": "vatgia.com",
        "url": "https://www.vatgia.com/user/login",
        "selectors": ["#username", "input[name='email']", "input[type='text']"]
    },
    {
        "name": "chovinh.com",
        "url": "https://chovinh.com/",
        "selectors": []
    },
    {
        "name": "cvt.vn",
        "url": "https://cvt.vn/login/",
        "selectors": ["input[name='login']", "input[name='username']", "input[type='text']"]
    }
]

async def inspect_site(site, p):
    print(f"\n==========================================")
    print(f"INSPECTING SITE: {site['name']}")
    print(f"URL: {site['url']}")
    print(f"==========================================")
    
    browser = await p.chromium.launch(headless=True)
    # Using a modern user agent
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 800},
        ignore_https_errors=True
    )
    page = await context.new_page()
    
    try:
        # Go to URL
        response = await page.goto(site['url'], wait_until="domcontentloaded", timeout=30000)
        print(f"  Response status: {response.status if response else 'No Response'}")
        await page.wait_for_timeout(3000)
        
        # Take screenshot of the page as loaded
        filename_loaded = f"inspect_{site['name'].replace('.', '_')}_loaded.png"
        await page.screenshot(path=filename_loaded)
        print(f"  📸 Saved screenshot: {filename_loaded}")
        
        # Check current URL (in case of redirects)
        current_url = page.url
        print(f"  Current URL: {current_url}")
        print(f"  Title: {await page.title()}")
        
        # If it's chovinh.com, let's find the login link since we loaded homepage
        if site['name'] == "chovinh.com":
            login_link = await page.locator("a:has-text('Đăng nhập'), a[href*='login'], a[href*='dang-nhap']").first.get_attribute("href")
            if login_link:
                target_url = login_link if login_link.startswith("http") else "https://chovinh.com/" + login_link.lstrip("/")
                print(f"  Found login link on chovinh.com: {target_url}")
                await page.goto(target_url, wait_until="domcontentloaded", timeout=20000)
                await page.wait_for_timeout(3000)
                await page.screenshot(path="inspect_chovinh_login_page.png")
                
        # Find all inputs
        inputs = await page.locator("input").all()
        print(f"  Total inputs found: {len(inputs)}")
        for idx, inp in enumerate(inputs[:20]):
            try:
                name = await inp.get_attribute("name") or ""
                id_attr = await inp.get_attribute("id") or ""
                type_attr = await inp.get_attribute("type") or ""
                placeholder = await inp.get_attribute("placeholder") or ""
                val = await inp.get_attribute("value") or ""
                is_vis = await inp.is_visible()
                print(f"    [{idx}] name='{name}', id='{id_attr}', type='{type_attr}', placeholder='{placeholder}', val='{val}', visible={is_vis}")
            except Exception as e_inp:
                print(f"    [{idx}] Error reading input: {e_inp}")
                
        # Let's try to fill the login form if we can identify inputs
        # Try to identify email/username input
        username_el = None
        password_el = None
        submit_el = None
        
        # 1. Look for password field
        pw_els = await page.locator("input[type='password']").all()
        if pw_els:
            password_el = pw_els[0]
            print(f"  Found password field: name='{await password_el.get_attribute('name')}'")
            
        # 2. Look for username/email field
        for sel in site['selectors'] + ["input[name='email']", "input[name='username']", "input[name='login']", "input[type='text']", "input[type='email']", "input[type='tel']"]:
            try:
                el = page.locator(sel).first
                if await el.count() > 0 and await el.is_visible():
                    username_el = el
                    print(f"  Found username field with selector: '{sel}'")
                    break
            except:
                pass
                
        # 3. Look for submit button
        for sel in ["button[type='submit']", "input[type='submit']", "button:has-text('Đăng nhập')", "button:has-text('Login')", "input:has-text('Đăng nhập')"]:
            try:
                el = page.locator(sel).first
                if await el.count() > 0 and await el.is_visible():
                    submit_el = el
                    print(f"  Found submit button with selector: '{sel}'")
                    break
            except:
                pass
                
        # Attempt Login if fields found
        if username_el and password_el:
            # Decide login identity (email, phone, or username)
            # Check placeholder or selector to see if it prefers phone or email
            user_val = EMAIL
            sel_name = await username_el.get_attribute("name") or ""
            placeholder_text = await username_el.get_attribute("placeholder") or ""
            
            if "phone" in sel_name.lower() or "dienthoai" in sel_name.lower() or "sđt" in placeholder_text.lower() or "điện thoại" in placeholder_text.lower():
                user_val = PHONE
            elif "username" in sel_name.lower() or "user" in sel_name.lower() or "tên" in placeholder_text.lower():
                # Some sites accept username or email
                user_val = EMAIL # default to email first, if fails we can try username or phone
                
            print(f"  Attempting login with: {user_val} / {PASSWORD}")
            await username_el.fill(user_val)
            await password_el.fill(PASSWORD)
            
            filename_filled = f"inspect_{site['name'].replace('.', '_')}_filled.png"
            await page.screenshot(path=filename_filled)
            print(f"  📸 Saved filled form screenshot: {filename_filled}")
            
            if submit_el:
                await submit_el.click()
            else:
                await password_el.press("Enter")
                
            await page.wait_for_timeout(6000)
            
            filename_after = f"inspect_{site['name'].replace('.', '_')}_after_login.png"
            await page.screenshot(path=filename_after)
            print(f"  📸 Saved after login click screenshot: {filename_after}")
            print(f"  URL after login click: {page.url}")
            
            # Let's inspect post button or post page URL
            # Look for post tin links: "Đăng tin", "post", "dang-tin"
            post_links = await page.locator("a:has-text('Đăng tin'), a[href*='dang-tin'], a[href*='post'], a[href*='dangtin']").all()
            print(f"  Total post-tin links found: {len(post_links)}")
            for pl in post_links[:10]:
                try:
                    text = await pl.inner_text()
                    href = await pl.get_attribute("href")
                    print(f"    Post Link: text='{text.strip()}', href='{href}'")
                except Exception as e_pl:
                    print(f"    Error reading post link: {e_pl}")
                    
            # Try to navigate directly to what we think is the posting page
            for post_path in ["/dang-tin.html", "/dang-tin", "/dangtin", "/post", "/user/post", "/classified/post"]:
                try:
                    target_post_url = site['url'].split("/")[0] + "//" + site['url'].split("/")[2] + post_path
                    print(f"  Trying direct navigation to post URL: {target_post_url}")
                    resp = await page.goto(target_post_url, wait_until="domcontentloaded", timeout=15000)
                    if resp and resp.status == 200:
                        await page.wait_for_timeout(3000)
                        filename_post = f"inspect_{site['name'].replace('.', '_')}_post_page.png"
                        await page.screenshot(path=filename_post)
                        print(f"    📸 Saved direct post page screenshot: {filename_post}")
                        print(f"    URL loaded: {page.url}")
                        
                        # Dump inputs of the post page
                        post_inputs = await page.locator("input, textarea, select").all()
                        print(f"    Inputs on post page: {len(post_inputs)}")
                        for p_idx, p_inp in enumerate(post_inputs[:25]):
                            p_tag = await p_inp.evaluate("el => el.tagName")
                            p_name = await p_inp.get_attribute("name") or ""
                            p_id = await p_inp.get_attribute("id") or ""
                            p_placeholder = await p_inp.get_attribute("placeholder") or ""
                            print(f"      [{p_idx}] <{p_tag}> name='{p_name}', id='{p_id}', placeholder='{p_placeholder}'")
                        break
                except Exception as e_post:
                    print(f"    Failed direct navigation to {post_path}: {e_post}")
                    
        else:
            print("  ❌ Could not identify username and password fields.")
            
    except Exception as e:
        print(f"  ❌ Error inspecting site: {e}")
    finally:
        await browser.close()

async def main():
    async with async_playwright() as p:
        # Inspect only the requested sites or all in sequence
        for site in SITES:
            await inspect_site(site, p)
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
