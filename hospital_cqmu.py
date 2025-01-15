from dotenv import load_dotenv
import os
import ast
from appium import webdriver
from appium.options.android import UiAutomator2Options

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
        self.size = self.driver.get_window_size()

if __name__ == "__main__":
    hospital = Hospital()
    print(1)