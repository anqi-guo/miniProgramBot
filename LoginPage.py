from BaseAutomation import BaseAutomation
import time

class LoginPage(BaseAutomation):
    def __init__(self, driver):
        super().__init__(driver)

    def is_login_required(self):
        return self.switch_window("login")

    def login(self):
        try:
            self.click_element("//div[contains(@class, 'wx-checkbox-input')]")
            self.click_element("//wx-button[contains(@class, 'login-btn')]")
            time.sleep(1)
            self.switch_window("phone-numbers")
            # TODO test this
            time.sleep(1)
            self.click_element("//wx-button[contains(@class, 'phone-tips')]")
        except Exception as e:
            print(f"Error during login: {e}")
            raise