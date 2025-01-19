import logging

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
        except TimeoutException as e:
            logging.error(f"Timeout while waiting for element with xpath")
            raise TimeoutException(f"Element not found within timeout for xpath")
        except NoSuchElementException as e:
            logging.error(f"Element not found")
            raise NoSuchElementException(f"Element not found")
        except Exception as e:
            logging.error(f"An error occurred")
            raise Exception(f"Unexpected error while waiting for element")

    def click_element(self, xpath):
        try:
            element = self.wait_for_element(xpath)
            element.click()
        except Exception as e:
            logging.error(f"Error clicking element with xpath {xpath}")
            raise

    def send_keys(self, xpath, keys, clear=True):
        try:
            input_area = self.wait_for_element(xpath)
            if clear:
                input_area.clear()  # Cross-platform way to clear text field
            input_area.send_keys(keys)
        except Exception as e:
            logging.error(f"Error sending keys to element with xpath {xpath}")
            raise

    def switch_window(self, title):
        try:
            for window in self.driver.window_handles:
                self.driver.switch_to.window(window)
                if title in self.driver.title:
                    return True
            logging.warning(f"No window found with title: {title}")
            return False
        except Exception as e:
            logging.error(f"Error switching window")
            raise