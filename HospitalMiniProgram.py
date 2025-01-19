import time
from selenium.common import NoSuchElementException, TimeoutException, WebDriverException, StaleElementReferenceException

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
        super().__init__(driver)
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

    def run(self):
        try:
            logging.info("Running")
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
        except (RecursionError, KeyError, NoSuchElementException, TimeoutException, WebDriverException, StaleElementReferenceException) as e:
            self.handle_error(e)
        except Exception as e:
            logging.error(f"Workflow failed with unexpected error: {e}")
            self.handle_error(e)

    def handle_error(self, e):
        try:
            errors = {
                NoSuchElementException: 'Element not found',
                TimeoutException: 'Operation time out',
                WebDriverException: 'Web driver issue',
                StaleElementReferenceException: 'Stale element not found in the current frame',
                KeyError: 'Key not found',
                RecursionError: 'Reached recursion limit',
            }

            error_message = errors.get(type(e), 'Unknown error occurred')
            logging.error(error_message)

            if type(e) == WebDriverException or type(e) == Exception:
                self.clear_cache()
            else:
                self.restart_program()
        except Exception:
            logging.error("Error on handling errors")

    def restart_program(self):
        try:
            logging.critical("Restarting mini program...")
            time.sleep(1)
            self.restart_cnt += 1
            self.driver.switch_to.context("NATIVE_APP")
            logging.info("restarting: switched context to NATIVE_APP")
            self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, "More").click()
            logging.info("restarting: clicked three dots")
            # click on "restart mini program"
            time.sleep(1)
            self.click_element("(//android.widget.ImageView[@resource-id='com.tencent.mm:id/h5n'])[10]")
            #self.driver.find_element(By.XPATH, "(//android.widget.ImageView[@resource-id='com.tencent.mm:id/h5n'])[10]").click()
            # rerun the searching process
            self.run()
        except Exception:
            logging.error("Error on restarting program")
            self.clear_cache()

    def clear_cache(self):
        try:
            logging.critical("clear cache: start")
            self.driver.switch_to.context("NATIVE_APP")
            try:
                # close mini program
                logging.info("clear cache: switched context to NATIVE_APP")
                self.click_element('(//android.widget.ImageButton[@content-desc="Close"])[2]')
            except NoSuchElementException:
                logging.info("clear cache: not in mini program")

            # click 我
            self.click_element('//android.widget.TextView[@resource-id="com.tencent.mm:id/icon_tv" and @text="我"]')
            # click 设置
            self.click_element('//*[@text="设置"]')
            # click 通用
            self.click_element('(//android.widget.LinearLayout[@resource-id="com.tencent.mm:id/oct"])[7]')
            # click 存储空间
            self.click_element('(//android.widget.LinearLayout[@resource-id="com.tencent.mm:id/oct"])[21]')
            # click 去清理
            self.click_element('//android.widget.Button[@resource-id="com.tencent.mm:id/pjh"]')
            # click 清理
            self.click_element('//android.widget.Button[@resource-id="com.tencent.mm:id/crz"]')
            # click 清理 in pop up window
            self.click_element('//android.widget.Button[@resource-id="com.tencent.mm:id/mm_alert_ok_btn"]')
            # click 返回
            for _ in range(4):
                self.click_element('//android.widget.ImageView[@content-desc="返回"]')
            # click 微信
            self.click_element('//android.widget.TextView[@resource-id="com.tencent.mm:id/icon_tv" and @text="微信"]')
            # run
            self.run()
        except Exception:
            logging.error("Error on clearing cache")

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