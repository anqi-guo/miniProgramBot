from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys

class BaseAutomation:
    def __init__(self, driver):
        self.driver = driver

    def wait_for_element(self, xpath=None, timeout=10, condition=None):
        try:
            if condition:
                WebDriverWait(self.driver, timeout).until(condition)
                return
            else:
                return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
        except TimeoutException:
            raise Exception("Element not found within timeout")

    def click_element(self, xpath):
        self.wait_for_element(xpath).click()

    def send_keys(self, xpath, keys, clear=True):
        input_area = self.wait_for_element(xpath)
        if clear:
            input_area.send_keys(Keys.COMMAND + "a")
            input_area.send_keys(Keys.DELETE)
        input_area.send_keys(keys)

    def switch_window(self, title):
        for window in self.driver.window_handles:
            self.driver.switch_to.window(window)
            if title in self.driver.title:
                return True
        return False