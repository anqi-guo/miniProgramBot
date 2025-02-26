from appium import webdriver
from appium.options.android import UiAutomator2Options
from dotenv import load_dotenv
import os
import ast
from HospitalMiniProgram import HospitalMiniProgram
import logging

load_dotenv()

BRANCH = os.getenv("BRANCH")
DEPARTMENT = os.getenv("DEPARTMENT")
SUBDEPARTMENT = os.getenv("SUBDEPARTMENT")
DOCTOR = os.getenv("DOCTOR")
CAPS = ast.literal_eval(os.getenv('CAPS'))
HEADERS = ast.literal_eval(os.getenv("HEADERS"))
ALARM = os.getenv("ALARM")

if __name__ == "__main__":
    while True:
        driver = webdriver.Remote(
                'http://localhost:4723',
                options=UiAutomator2Options().load_capabilities(CAPS)
            )
        logging.critical("Driver created")
        mini_program = HospitalMiniProgram(driver, BRANCH, DEPARTMENT, SUBDEPARTMENT, DOCTOR, HEADERS, ALARM)
        mini_program.run()
        logging.critical("Driver ended")