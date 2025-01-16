from dotenv import load_dotenv
import os
import ast
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import requests
import easyocr

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
        self.search_cnt = 0

    def to_hospital(self):
        #self.switch()
        # click 门诊挂号
        WebDriverWait(self.driver, 100).until(EC.presence_of_element_located((By.XPATH, '//*[@text="门诊挂号"]')))
        self.driver.find_element(By.XPATH, '//*[@text="门诊挂号"]').click()
        # click 院区
        WebDriverWait(self.driver, 100).until(EC.presence_of_element_located((By.XPATH, '//*[@text="本部院区"]')))
        self.driver.find_element(By.XPATH, f'//*[@text="{HOSPITAL}"]').click()
        # click 确定
        time.sleep(5)
        self.driver.find_element(By.XPATH, '//*[contains(@text,"阅读并同意挂号预约须知")]').click()
        self.driver.find_element(By.XPATH, '//*[@text="确定"]').click()

    def to_department(self):
        WebDriverWait(self.driver, 100).until(
            EC.presence_of_element_located((By.XPATH, '//*[contains(@text,"产科门诊")]')))
        # click department
        swipe_down_cnt = 0
        while True:
            try:
                self.driver.find_element(By.XPATH, f'//*[@text="{DEPARTMENT}"]').click()
                break
            except NoSuchElementException:
                if swipe_down_cnt <= 4:
                    self.driver.swipe(
                        self.size['width'] * 0.1,
                        self.size['height'] * 0.9,
                        self.size['width'] * 0.1,
                        self.size['height'] * 0.6
                    )
                    swipe_down_cnt += 1
                else:
                    self.driver.swipe(
                        self.size['width'] * 0.1,
                        self.size['height'] * 0.1,
                        self.size['width'] * 0.1,
                        self.size['height'] * 0.9
                    )
                    swipe_down_cnt = 0

        # click subdepartment
        elements = self.driver.find_elements(By.XPATH, f'//*[@text="{SUBDEPARTMENT}"]')
        elements[-1].click()

    def check_availability(self):
        WebDriverWait(self.driver, 100).until(EC.presence_of_element_located((By.XPATH, '//*[contains(@text,"只看有号")]')))
        # click the doctor
        while True:
            try:
                self.driver.find_element(By.XPATH, f'//*[contains(@text,"{DOCTOR}")]').click()
                break
            except NoSuchElementException:
                self.driver.swipe(
                    self.size['width'] * 0.5,
                    self.size['height'] * 0.9,
                    self.size['width'] * 0.5,
                    self.size['height'] * 0.1
                )

        WebDriverWait(self.driver, 100).until(EC.presence_of_element_located((By.XPATH, f'//*[contains(@text,"{DOCTOR}")]')))
        dates = self.driver.find_elements(By.XPATH, '//*[contains(@text,"星期")]')
        for date in dates:
            if "有号" in date.text:
                self.reserve(date)
                return

        try:
            swipe_y = dates[0].rect['y'] + dates[0].rect['height'] * 0.5
            self.driver.swipe(self.size['width'] * 0.9, swipe_y, self.size['width'] * 0.1, swipe_y)
            dates = self.driver.find_elements(By.XPATH, '//*[contains(@text,"星期")]')
            for date in dates[-2:]:
                if "有号" in date.text:
                    self.reserve(date)
                    return
        except IndexError:
            self.driver.back()
            self.driver.back()
            self.search()
            return

        # search again
        self.driver.back()
        self.driver.back()
        self.search()

    def reserve(self, date):
        #playsound()
        print("有号")
        # click date that has slots
        date.click()
        # click the first slot
        WebDriverWait(self.driver, 100).until(EC.presence_of_element_located((By.XPATH, '//*[contains(@text, "余 ")]')))
        self.driver.find_element(By.XPATH, '//*[contains(@text, "余 ")]').click()
        # confirm
        self.to_confirm()

    def switch(self):
        # switch to webview
        self.driver.switch_to.context('WEBVIEW_com.tencent.mm:appbrand0')
        for i, window in enumerate(self.driver.window_handles):
            self.driver.switch_to.window(window)
            if self.driver.title == '预约信息':
                break

    def to_confirm(self):
        WebDriverWait(self.driver, 100).until(
            EC.presence_of_element_located((By.XPATH, '//*[contains(@text, "初诊")]')))
        # click 初诊
        self.driver.find_element(By.XPATH, '//*[contains(@text, "初诊")]').click()

        self.switch()

        while True:
            try:
                # send verification code
                self.send_verification_code()
                time.sleep(1)
                # click confirm
                self.driver.find_element(By.XPATH, '//*[contains(@class,"bt2")]').click()
                # if it fails to go to the next page then refresh the image
                self.refresh_image()
            except NoSuchElementException:
                break
            finally:
                print("Done!")

    def refresh_image(self):
        self.driver.find_elements(By.XPATH, '//*[contains(@class,"img1")]//img')[-1].click()

    def send_verification_code(self):
        # get the image
        while True:
            try:
                # wait for image to load
                time.sleep(1)
                broken_image = self.driver.find_element(By.XPATH, '//*[contains(@class,"van-image__error")]')
                broken_image.click()
            except NoSuchElementException:
                break

        # wait for image to load
        time.sleep(1)
        image = self.driver.find_elements(By.XPATH, '//*[contains(@class,"img1")]//img')[-1]
        image_url = image.get_attribute('src')

        # download the image
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(image_url, headers=headers, stream=True)
        if response.status_code == 200:
            with open("image.jpg", "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            # OCR
            reader = easyocr.Reader(['en'])
            result = reader.readtext('image.jpg', allowlist='0123456789')

            if not result: # fail to identify anything
                self.refresh_image()
                self.send_verification_code()
            else:
                code = result[0][1]
                if len(code) >= 4:
                    # send the code
                    input_area = self.driver.find_element(By.XPATH, '//*[@placeholder="请输入"]')
                    input_area.send_keys(Keys.COMMAND + "a")
                    input_area.send_keys(Keys.DELETE)
                    input_area.send_keys(code[-4:])
                else: # fail to identify 4 digits
                    self.refresh_image()
                    self.send_verification_code()
        else: # fail to retrieve the image
            self.refresh_image()
            self.send_verification_code()

    def search(self):
        self.search_cnt += 1
        print(self.search_cnt, time.ctime())
        self.to_department()
        self.check_availability()
        self.to_confirm()

if __name__ == "__main__":
    hospital = Hospital()
    hospital.to_hospital()
    hospital.search()
