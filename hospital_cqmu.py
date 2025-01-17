from appium.webdriver.common.appiumby import AppiumBy
from dotenv import load_dotenv
import os
import ast
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import requests
import easyocr

load_dotenv()
HOSPITAL = os.getenv("HOSPITAL")
DEPARTMENT = os.getenv("DEPARTMENT")
SUBDEPARTMENT = os.getenv("SUBDEPARTMENT")
DOCTOR = os.getenv("DOCTOR")
CAPS = ast.literal_eval(os.getenv('CAPS'))
HEADERS = ast.literal_eval(os.getenv("HEADERS"))

class Hospital:
    def __init__(self):
        self.driver = webdriver.Remote(
            'http://localhost:4723',
            options=UiAutomator2Options().load_capabilities(CAPS)
        )
        # device window size
        self.size = self.driver.get_window_size()
        self.search_cnt = 0
        self.first_send = True
        self.reader = easyocr.Reader(["en"])

    def wait_for_element(self, xpath=None, timeout=20, condition=None):
        """Wait for an element to meet the specified condition."""
        try:
            if condition:
                WebDriverWait(self.driver, timeout).until(condition)
                return
            else:
                return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
        except TimeoutException:
            self.quit()


    def click_element(self, xpath):
        """Click an element after waiting for its presence."""
        self.wait_for_element(xpath).click()

    def send_keys_to_element(self, xpath, keys):
        """Send keys to an input field."""
        input_area = self.wait_for_element(xpath)
        if not self.first_send:
            input_area.send_keys(Keys.CONTROL + "a")
            input_area.send_keys(Keys.DELETE)
        input_area.send_keys(keys)
        self.first_send = False

    def homepage(self):
        # click 门诊挂号
        self.click_element('//*[@text="门诊挂号"]')

    def book_page(self):
        self.driver.switch_to.context('WEBVIEW_com.tencent.mm:appbrand0')
        self.switch_window("预约挂号")

        self.restart_program()

        self.click_element(f'//span[text()="{HOSPITAL}"]')
        # click 确定
        self.switch_window("预约挂号须知")

        self.wait_for_element(condition=lambda driver: driver.find_element(By.XPATH, "//span[text()='(0s)']").get_attribute(
                "style") == "display: none;")

        # click checkbox
        self.click_element("//span[text()='阅读并同意挂号预约须知']")
        # click confirm
        self.click_element("//button[.//div//span[text()='确定']]")

    def choose_department_page(self):
        self.switch_window("选择科室")
        try:
            self.wait_for_element(xpath="//div[@class='leftNav van-sidebar']//a")

            department_elements = self.driver.find_elements(By.XPATH, "//div[@class='leftNav van-sidebar']//a")
            for element in department_elements:
                if element.find_element(By.XPATH, ".//div[@class='van-sidebar-item__text']").text == DEPARTMENT:
                    element.click()
                    subdepartment_elements = self.driver.find_elements(By.XPATH, "//div[@class='van-cell-group van-hairline--top-bottom']//div//div//span")
                    for span in subdepartment_elements:
                        if span.text == SUBDEPARTMENT:
                            span.click()
                            return
        except Exception as e:
            print(e)
            self.restart_program()

    def choose_doctor_page(self):
        try:
            self.wait_for_element(xpath="//div[@class='one']//div//div//span[@class='name']")
            doctor_elements = self.driver.find_elements(By.XPATH, "//div[@class='one']//div//div//span[@class='name']")
            for span in doctor_elements:
                if span.text == DOCTOR:
                    span.click()
                    return
        except NoSuchElementException:
            print("找不到医生")
            self.restart_program()

    def choose_time_page(self):
        while True:
            try:
                self.switch_window("选择时间")
                tablist = self.wait_for_element("//div[@role='tablist']")
                for tab in tablist.find_elements(By.XPATH, ".//div[@role='tab']"):
                    if "有号" in tab.text:
                        tab.click()
                        self.wait_for_element("//div[contains(@class, 'selectTimeBoxActive')]").click()
                        self.booking_info_page()
                        return

                self.retry_search(back_attempts=2)
            except Exception as e:
                print(e)
                self.restart_program()

    def booking_info_page(self):
        #print("预约信息")
        time.sleep(1)
        self.click_element("//span[text()='初诊']")
        while True:
            try:
                self.send_verification_code()
                time.sleep(10)
                self.click_element("//button[.//span[text()='确认预约']]")
                self.refresh_image()
            except Exception as e:
                print(e)
                self.retry_search(back_attempts=3)

    def refresh_image(self):
        self.driver.find_elements(By.XPATH, '//*[contains(@class,"img1")]//img')[-1].click()

    def send_verification_code(self):
        # get the image
        while True:
            try:
                # step 1: check for broken image
                time.sleep(1)
                try:
                    broken_image = self.driver.find_element(By.XPATH, '//*[contains(@class,"van-image__error")]')
                    # step 2: refresh by clicking on the broken image
                    broken_image.click()
                    continue # restart loop for the refresh
                except NoSuchElementException:
                    pass # no broken image found, proceed to the next step

                # step 3: wait for the unbroken image to load and get the url
                self.wait_for_element("//div[contains(@class, 'van-field')]//div//img")
                image_url = self.driver.find_element(By.XPATH,
                                                     "//div[contains(@class, 'van-field')]//div//img").get_attribute('src')
                if not image_url:
                    self.refresh_image()
                    continue

                # step 4: download the image
                response = requests.get(image_url, headers=HEADERS, stream=True)
                if response.status_code != 200:
                    self.refresh_image()
                    continue

                with open("image.jpg", "wb") as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)

                # step 5: perform OCR
                result = self.reader.readtext('image.jpg', allowlist='0123456789')

                if not result:
                    # step 6: no text found
                    self.refresh_image()
                    continue

                # step 7: validate and process the text
                code = result[0][1]
                if len(code) >= 4:
                    # send the code
                    input_area = self.driver.find_element(By.XPATH, '//*[@placeholder="请输入"]')
                    if self.first_send:
                        self.first_send = False
                    else:
                        input_area.send_keys(Keys.COMMAND + "a")
                        input_area.send_keys(Keys.DELETE)
                    input_area.send_keys(code[-4:])
                    break
                else:  # fail to identify 4 digits
                    # print("识别少于4位数")
                    self.refresh_image()
                    continue
            except Exception as e:
                print(e)
                self.restart_program()

    def search(self):
        self.search_cnt += 1
        print(self.search_cnt, time.ctime())
        self.choose_department_page()
        self.choose_doctor_page()
        self.choose_time_page()

    def retry_search(self, back_attempts):
        if self.search_cnt < 300:
            for i in range(back_attempts):
                self.driver.back()
            self.search()
        else:
            self.quit()

    def restart_program(self):
        self.driver.switch_to.context("NATIVE_APP")
        self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, "More").click()
        time.sleep(1)
        self.click_element("(//android.widget.ImageView[@resource-id='com.tencent.mm:id/h5n'])[10]")
        self.run()

    def run(self):
        self.homepage()
        self.book_page()
        self.search()

    def switch_window(self, title):
        for i, window in enumerate(self.driver.window_handles):
            self.driver.switch_to.window(window)
            if self.driver.title == title:
                break

    def quit(self):
        for i in range(4):
            self.driver.back()
        self.driver.switch_to.context("NATIVE_APP")
        self.driver.back()

        try:
            # Add a check if the driver is active or not
            if self.driver:
                self.driver.quit()
        except Exception as e:
            print(f"Error quitting the session: {e}")