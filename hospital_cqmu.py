from dotenv import load_dotenv
import os
import ast
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time

load_dotenv()
HOSPITAL = os.getenv("HOSPITAL")
DEPARTMENT = os.getenv("DEPARTMENT")
SUBDEPARTMENT = os.getenv("SUBDEPARTMENT")
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

    def to_hospital(self):
        # click 门诊挂号
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@text="门诊挂号"]')))
        self.driver.find_element(By.XPATH, '//*[@text="门诊挂号"]').click()
        # click 院区
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@text="本部院区"]')))
        self.driver.find_element(By.XPATH, f'//*[@text="{HOSPITAL}"]').click()
        # click 确定
        time.sleep(6)
        self.driver.find_element(By.XPATH, '//*[contains(@text,"阅读并同意挂号预约须知")]').click()
        self.driver.find_element(By.XPATH, '//*[@text="确定"]').click()

    def to_department(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[contains(@text,"产科门诊")]')))
        # click department
        while True:
            try:
                self.driver.find_element(By.XPATH, f'//*[@text="{DEPARTMENT}"]').click()
                break
            except NoSuchElementException:
                self.driver.swipe(
                    self.size['width'] * 0.1,
                    self.size['height'] * 0.9,
                    self.size['width'] * 0.1,
                    self.size['height'] * 0.6
                )
        # click subdepartment
        elements = self.driver.find_elements(By.XPATH, f'//*[@text="{SUBDEPARTMENT}"]')
        elements[-1].click()

if __name__ == "__main__":
    hospital = Hospital()
    #hospital.to_hospital()
    hospital.to_department()
    print(1)