from appium import webdriver
from appium.options.android import UiAutomator2Options
from dotenv import load_dotenv
import os
import ast
from HospitalMiniProgram import HospitalMiniProgram

load_dotenv()

BRANCH = os.getenv("BRANCH")
DEPARTMENT = os.getenv("DEPARTMENT")
SUBDEPARTMENT = os.getenv("SUBDEPARTMENT")
DOCTOR = os.getenv("DOCTOR")
CAPS = ast.literal_eval(os.getenv('CAPS'))
HEADERS = ast.literal_eval(os.getenv("HEADERS"))

if __name__ == "__main__":
    driver = webdriver.Remote(
            'http://localhost:4723',
            options=UiAutomator2Options().load_capabilities(CAPS)
        )
    mini_program = HospitalMiniProgram(driver, BRANCH, DEPARTMENT, SUBDEPARTMENT, DOCTOR, HEADERS)
    mini_program.run()
    driver.quit()