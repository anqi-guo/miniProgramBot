from dotenv import load_dotenv
import os
import ast
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By

load_dotenv()
DEPARTMENT = os.getenv("DEPARTMENT")
DOCTOR = os.getenv("DOCTOR")
CAPS = ast.literal_eval(os.getenv('CAPS'))

class Hospital:
    def __init__(self):
        self.driver = webdriver.Remote(
            'http://localhost:4723',
            options=UiAutomator2Options().load_capabilities(CAPS)
        )
        # device window size
        self.size = self.driver.get_window_size()
    def enter_program(self):
        # swipe
        self.driver.flick(
            self.size['width'] * 0.5,
            self.size['height'] * 0.4,
            self.size['width'] * 0.5,
            self.size['height'] * 0.9
        )
        # click on hospital icon
        self.driver.find_element(By.XPATH, '//*[@text="重医一院"]').click()

if __name__ == "__main__":
    hospital = Hospital()
    hospital.enter_program()
    print(1)