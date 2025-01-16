from dotenv import load_dotenv
import os
import ast
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
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
        self.first_type = True

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
        self.driver.switch_to.context('WEBVIEW_com.tencent.mm:appbrand0')
        self.switch_window("选择科室")

        WebDriverWait(self.driver, 100).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='leftNav van-sidebar']//a")))
        # click department
        a_elements = self.driver.find_elements(By.XPATH, "//div[@class='leftNav van-sidebar']//a")
        for a in a_elements:
            text = a.find_element(By.XPATH, ".//div[@class='van-sidebar-item__text']").text
            if text == DEPARTMENT:
                a.click()
                span_elements = self.driver.find_elements(By.XPATH,
                                                     "//div[@class='van-cell-group van-hairline--top-bottom']//div//div//span")
                for span in span_elements:
                    if span.text == SUBDEPARTMENT:
                        span.click()
                        return
        print("error")

    def check_availability(self):
        self.switch_window("选择科室")
        print("选择科室")
        #WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//span[@class="labelName" and text()="只看有号"]')))
        time.sleep(5)
        # Find all <span> elements with class 'name' using XPath
        span_elements = self.driver.find_elements(By.XPATH, "//div[@class='one']//div//div//span[@class='name']")
        for span in span_elements:
            if span.text == DOCTOR:
                span.click()

        self.switch_window("选择时间")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@role='tablist']")))
        # Find the parent div with role="tablist"
        tablist = self.driver.find_element(By.XPATH, "//div[@role='tablist']")
        # Find all div elements with role="tab" inside the tablist
        tabs = tablist.find_elements(By.XPATH, ".//div[@role='tab']")
        # Loop through each tab and extract the relevant text
        for tab in tabs:
            status = tab.find_element(By.XPATH, ".//div[contains(@class, 'color3') or contains(@class, 'has')]").text
            if status == "有号":
                tab.click()
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'selectTimeBoxActive')]")))
                self.driver.find_element(By.XPATH, "//div[contains(@class, 'selectTimeBoxActive')]").click()
                self.to_confirm()
                return

        # search again
        # TODO test this part
        self.driver.back()
        self.driver.back()
        self.search()

    def switch_window(self, title):
        for i, window in enumerate(self.driver.window_handles):
            self.driver.switch_to.window(window)
            if self.driver.title == title:
                break

    def to_confirm(self):
        self.switch_window("预约信息")

        WebDriverWait(self.driver, 100).until(
            EC.presence_of_element_located((By.XPATH, '//span[text()="初诊"]')))
        # click 初诊
        self.driver.find_element("xpath", "//span[text()='初诊']").click()

        while True:
            try:
                # send verification code
                self.send_verification_code()
                time.sleep(1)
                # click confirm
                #self.driver.find_element(By.XPATH, '//*[contains(@class,"bt2")]').click()
                # if it fails to go to the next page then refresh the image
                self.refresh_image()
            except NoSuchElementException:
                break

    def refresh_image(self):
        self.driver.find_elements(By.XPATH, '//*[contains(@class,"img1")]//img')[-1].click()

    def send_verification_code(self):
        # get the image
        while True:
            try:
                # wait for image to load
                time.sleep(1)
                broken_image = self.driver.find_element(By.XPATH, '//*[contains(@class,"van-image__error")]')
                print("click broken page")
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
                print("no digit")
                self.refresh_image()
                self.send_verification_code()
            else:
                code = result[0][1]
                print(code)
                if len(code) >= 4:
                    # send the code
                    input_area = self.driver.find_element(By.XPATH, '//*[@placeholder="请输入"]')
                    if self.first_type:
                        self.first_type = False
                    else:
                        input_area.send_keys(Keys.COMMAND + "a")
                        input_area.send_keys(Keys.DELETE)

                    input_area.send_keys(code[-4:])
                else: # fail to identify 4 digits
                    print("less than 4 digits")
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

