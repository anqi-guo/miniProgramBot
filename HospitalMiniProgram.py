import time
from selenium.common import NoSuchElementException, TimeoutException, WebDriverException

from BaseAutomation import BaseAutomation
from Booking import Booking
from Hompage import Homepage
from LoginPage import LoginPage
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By
import logging
from log import setup_logging

# initialize logging
setup_logging()

class HospitalMiniProgram(BaseAutomation):
    def __init__(self, driver, branch, department, subdepartment, doctor, headers):
        self.driver = driver
        self.headers = headers
        self.branch = branch
        self.department = department
        self.subdepartment = subdepartment
        self.doctor = doctor
        self.homepage = Homepage(driver)
        self.login_page = LoginPage(driver)
        self.booking = Booking(driver, headers)
        self.search_cnt = 0
        self.restart_cnt = 0

    def run(self):
        try:
            # ensure the mini program is open
            if not self.homepage.is_open():
                self.homepage.open_mini_program()

            # start outpatient registration
            self.homepage.outpatient_registration()
            self.restart_cnt = 0

            # handle login if required
            if self.login_page.is_login_required():
                self.login_page.login()

            # select branch
            self.booking.select_branch(self.branch)

            # attempt booking
            while True:
                # select department
                self.booking.select_department(self.department, self.subdepartment)
                # select doctor
                self.booking.select_doctor(self.doctor)
                # select time
                if self.booking.select_time():
                    break # if there are available slot, then quit the while loop
                else:
                    self.retry_search() # go back to the select department page and retry search
        except (RecursionError, KeyError, NoSuchElementException, TimeoutException, WebDriverException) as e:
            self.handle_error(e)
        except Exception as e:
            logging.error(f"Workflow failed with unexpected error: {e}")
            self.handle_error(e)

    def handle_error(self, e):
        errors = {
            RecursionError: 'Reached recursion limit',
            NoSuchElementException: 'Element not found',
            TimeoutException: 'Operation time out',
            WebDriverException: 'Web driver issue',
            KeyError: 'Key not found'
        }

        error_message = errors.get(type(e), 'Unknown error occurred')
        logging.error(f'Error: {error_message}')

        if self.restart_cnt < 4:
            self.restart_cnt += 1
            self.restart_program()
        else:
            self.clear_cache()

    def restart_program(self):
        logging.info("Restarting mini program...")
        self.restart_cnt += 1
        self.driver.switch_to.context("NATIVE_APP")
        self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, "More").click()
        # click on "restart mini program"
        time.sleep(1)
        self.click_element("(//android.widget.ImageView[@resource-id='com.tencent.mm:id/h5n'])[10]")
        #self.driver.find_element(By.XPATH, "(//android.widget.ImageView[@resource-id='com.tencent.mm:id/h5n'])[10]").click()
        # rerun the searching process
        self.run()

    def clear_cache(self):
        self.driver.switch_to.context("NATIVE_APP")
        # close mini program
        self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, "More").click() # TODO change to close button
        # click 我
        self.click_element('//android.widget.TextView[@resource-id="com.tencent.mm:id/icon_tv" and @text="我"]')
        #self.driver.find_element(By.XPATH, '//android.widget.TextView[@resource-id="com.tencent.mm:id/icon_tv" and @text="我"]').click()
        # click 设置
        self.click_element('//*[@text="设置"]')
        #self.driver.find_element(By.XPATH, '//*[@text="设置"]').click()
        # click 通用
        self.click_element('(//android.widget.LinearLayout[@resource-id="com.tencent.mm:id/oct"])[7]')
        #self.driver.find_element(By.XPATH, '(//android.widget.LinearLayout[@resource-id="com.tencent.mm:id/oct"])[7]').click()
        # click 存储空间
        self.click_element('(//android.widget.LinearLayout[@resource-id="com.tencent.mm:id/oct"])[21]')
        #self.driver.find_element(By.XPATH, '(//android.widget.LinearLayout[@resource-id="com.tencent.mm:id/oct"])[21]').click()
        # click 去清理
        self.click_element('//android.widget.Button[@resource-id="com.tencent.mm:id/pjh"]')
        #self.driver.find_element(By.XPATH, '//android.widget.Button[@resource-id="com.tencent.mm:id/pjh"]').click()
        # click 清理
        self.click_element('//android.widget.Button[@resource-id="com.tencent.mm:id/crz"]')
        #self.driver.find_element(By.XPATH, '//android.widget.Button[@resource-id="com.tencent.mm:id/crz"]').click()
        # click 清理 in pop up window
        self.click_element('//android.widget.Button[@resource-id="com.tencent.mm:id/mm_alert_ok_btn"]')
        #self.driver.find_element(By.XPATH, '//android.widget.Button[@resource-id="com.tencent.mm:id/mm_alert_ok_btn"]').click()
        # click 返回
        for _ in range(4):
            self.click_element('//android.widget.ImageView[@content-desc="返回"]')
        #self.driver.find_element(By.XPATH, '//android.widget.ImageView[@content-desc="返回"]').click()
        # click 微信
        self.click_element('//android.widget.TextView[@resource-id="com.tencent.mm:id/icon_tv" and @text="微信"]')
        #self.driver.find_element(By.XPATH, '//android.widget.TextView[@resource-id="com.tencent.mm:id/icon_tv" and @text="微信"]').click()
        # run
        self.run()

    def retry_search(self):
        self.search_cnt += 1
        logging.info(f"Search attempt {self.search_cnt}")
        for _ in range(2):
            self.driver.back()

    def quit_program(self):
        for _ in range(6):
            self.driver.back()
        self.driver.switch_to.context("NATIVE_APP")
        self.driver.back()
        try:
            # Add a check if the driver is active or not
            if self.driver:
                self.driver.quit()
                #self.driver = None
        except Exception as e:
            logging.error(f"Error quitting the session: {e}")
            raise