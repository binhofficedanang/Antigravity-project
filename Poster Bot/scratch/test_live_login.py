import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_automation import WebAutomation

def main():
    bot = WebAutomation(headless=True)
    bot.start()
    
    # Credentials from config
    username = "binhofficedanang"
    password = "Binh1995@"
    
    try:
        print("\n--- Testing Login: 123nhadatviet.com ---")
        login_123 = bot.login_123nhadatviet(username, password)
        print(f"Login 123nhadatviet.com success: {login_123}")
        bot.safe_screenshot(os.path.join(os.path.dirname(__file__), "login_123nhadatviet_result.png"))
        
        print("\n--- Testing Login: nhadatviet247.net ---")
        login_247 = bot.login_nhadatviet247(username, password)
        print(f"Login nhadatviet247.net success: {login_247}")
        bot.safe_screenshot(os.path.join(os.path.dirname(__file__), "login_nhadatviet247_result.png"))
        
    except Exception as e:
        print("Error during login test:", e)
    finally:
        bot.stop()

if __name__ == "__main__":
    main()
