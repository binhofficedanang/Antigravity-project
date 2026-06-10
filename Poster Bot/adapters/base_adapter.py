from abc import ABC, abstractmethod

class BaseSiteAdapter(ABC):
    def __init__(self, automation):
        """
        automation: an instance of the WebAutomation class to access global Playwright
        objects (like self.automation.page, self.automation.context) and shared utilities
        (like safe_screenshot, solve_turnstile_captcha, etc.)
        """
        self.automation = automation

    @abstractmethod
    def login(self, username, password) -> bool:
        """
        Login to the target site. Returns True if login was successful, False otherwise.
        """
        pass

    @abstractmethod
    def post(self, item) -> bool:
        """
        Fill and submit the property listing form. Returns True if post succeeded, False otherwise.
        """
        pass
