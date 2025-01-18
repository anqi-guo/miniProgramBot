from BaseAutomation import BaseAutomation
import time
from selenium.webdriver.common.by import By

class LoginPage(BaseAutomation):
    def __init__(self, driver):
        super().__init__(driver)

    def is_login_required(self):
        return self.switch_window("login")

    def login(self):
        for window in self.driver.window_handles:
            self.driver.switch_to.window(window)
            if "login" in self.driver.title:
                break
        # click on checkbox
        self.driver.find_element(By.TAG_NAME, "wx-checkbox-group").click()
        # click on login button
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, "wx-button.login-btn").click()
        time.sleep(1)
        # a window pops from bottom
        for window in self.driver.window_handles:
            self.driver.switch_to.window(window)
            if "getUserPhoneNumberForWXLib" in self.driver.title:
                break
        # click on phone number
        time.sleep(2)
        self.driver.find_element(By.XPATH, "//wx-view[contains(@class, 'phone-num')]").click()