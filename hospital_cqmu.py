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

    def check_availability(self):
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//*[contains(@text,"{SUBDEPARTMENT}")]')))
        # 只看有号
        #self.driver.find_element(By.XPATH, '//*[@text="只看有号"]/following-sibling::*').click()
        # click the doctor
        # while True:
        #     try:
        #         self.driver.find_element(By.XPATH, f'//*[contains(@text,"{DOCTOR}")]').click()
        #         break
        #     except NoSuchElementException:
        #         self.driver.swipe(
        #             self.size['width'] * 0.5,
        #             self.size['height'] * 0.9,
        #             self.size['width'] * 0.5,
        #             self.size['height'] * 0.1
        #         )

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//*[contains(@text,"{DOCTOR}")]')))
        dates = self.driver.find_elements(By.XPATH, '//*[contains(@text,"星期")]')
        for date in dates:
            if "有号" in date.text:
                self.reserve(date)
                return

        swipe_y = dates[3].rect['y'] + dates[3].rect['height'] * 0.5
        self.driver.swipe(self.size['width'] * 0.9, swipe_y, self.size['width'] * 0.1, swipe_y)
        dates = self.driver.find_elements(By.XPATH, '//*[contains(@text,"星期")]')
        for date in dates[-2:]:
            if "有号" in date.text:
                self.reserve(date)
                return

        # TODO refresh

    def reserve(self, date):
        # click date that has slots
        date.click()
        # click the first slot
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[contains(@text, "余 ")]')))
        self.driver.find_element(By.XPATH, '//*[contains(@text, "余 ")]').click()
        # click 初诊
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//*[contains(@text, "{DOCTOR}")]')))
        self.driver.find_element(By.XPATH, '//*[contains(@text,"初诊")]').click()

if __name__ == "__main__":
    hospital = Hospital()
    #hospital.to_hospital()
    #hospital.to_department()
    hospital.check_availability()
    print(1)