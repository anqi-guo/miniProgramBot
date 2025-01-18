import time

from selenium.common import WebDriverException

from BaseAutomation import BaseAutomation
from selenium.webdriver.common.by import By
from verification_handler import VerificationHandler
from log import setup_logging
import logging

# initialize logging
setup_logging()

class Booking(BaseAutomation):
    def __init__(self, driver, headers):
        super().__init__(driver)
        self.verification_handler = VerificationHandler(driver, headers)

    def select_branch(self, branch):
        try:
            self.switch_window("预约挂号")
            self.click_element(f"//div[div/span[text()='{branch}']]")
            self.switch_window("预约挂号须知")
            self.wait_for_element(
                condition=lambda driver: driver.find_element(By.XPATH, "//span[text()='(0s)']").get_attribute(
                    "style") == "display: none;")
            # click checkbox
            self.click_element("//span[text()='阅读并同意挂号预约须知']")
            # click confirm
            self.click_element("//button[.//div//span[text()='确定']]")
        except WebDriverException:
            logging.error("Error selecting branch: web driver issue")
        except Exception as e:
            logging.error(f"Error selecting branch: {e}")
            raise

    def select_department(self, department, subdepartment):
        try:
            self.switch_window("选择科室")
            self.wait_for_element("//div[@class='leftNav van-sidebar']//a")
            department_elements = self.driver.find_elements(By.XPATH, "//div[@class='leftNav van-sidebar']//a")
            for element in department_elements:
                if element.find_element(By.XPATH, ".//div[@class='van-sidebar-item__text']").text == department:
                    element.click()
                    subdepartment_elements = self.driver.find_elements(By.XPATH,
                                                                       "//div[@class='van-cell-group van-hairline--top-bottom']//div//div//span")
                    for span in subdepartment_elements:
                        if span.text == subdepartment:
                            span.click()
                            return
        except WebDriverException:
            logging.error("Error selecting department: web driver issue")
        except Exception as e:
            logging.error(f"Error selecting department: {e}")
            raise

    def select_doctor(self, doctor):
        try:
            self.wait_for_element(xpath="//div[@class='one']//div//div//span[@class='name']")
            doctor_elements = self.driver.find_elements(By.XPATH, "//div[@class='one']//div//div//span[@class='name']")
            for span in doctor_elements:
                if span.text == doctor:
                    span.click()
                    return
        except WebDriverException:
            logging.error("Error selecting doctor: web driver issue")
        except Exception as e:
            logging.error(f"Error selecting doctor: {e}")
            raise

    def select_time(self):
        try:
            self.switch_window("选择时间")
            tablist = self.wait_for_element("//div[@role='tablist']")
            for tab in tablist.find_elements(By.XPATH, ".//div[@role='tab']"):
                if "有号" in tab.text:
                    tab.click()
                    self.click_element("//div[contains(@class, 'selectTimeBoxActive')]")
                    # next page
                    self.confirm_booking()
                    return True
            return False
        except WebDriverException:
            logging.error("Error selecting time: web driver issue")
        except Exception as e:
            logging.error(f"Error selecting time: {e}")
            raise

    def confirm_booking(self):
        while True:
            try:
                self.verification_handler.send_verification_code()
                self.click_element("//span[text()='初诊']")
                self.click_element("//button[.//span[text()='确认预约']]")
                self.verification_handler.refresh_image()
            except WebDriverException:
                logging.error("Error confirm booking: web driver issue")
            except Exception as e:
                logging.error(f"Error confirming booking: {e}")
                raise