import time

from Booking import Booking
from Hompage import Homepage
from LoginPage import LoginPage
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By


class HospitalMiniProgram:
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

    def run(self):
        try:
            if not self.homepage.is_open():
                self.homepage.open_mini_program()

            self.homepage.outpatient_registration()
            if self.login_page.is_login_required():
                self.login_page.login()
            self.booking.select_branch(self.branch)
            while True:
                self.booking.select_department(self.department, self.subdepartment)
                self.booking.select_doctor(self.doctor)
                if self.booking.select_time():
                    break
                else:
                    self.retry_search()
        except RecursionError as e:
            print(e)
            self.quit_program()
        except Exception as e:
            print(f"Workflow failed: {e}")
            if self.driver:
                self.restart_program()

    def restart_program(self):
        print("Restarting mini program...")
        self.driver.switch_to.context("NATIVE_APP")
        self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, "More").click()
        # click on "restart mini program"
        time.sleep(1)
        self.driver.find_element(By.XPATH, "(//android.widget.ImageView[@resource-id='com.tencent.mm:id/h5n'])[10]").click()
        # rerun the searching process
        self.run()

    def retry_search(self):
        self.search_cnt += 1
        print(self.search_cnt, time.ctime())
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
            print(f"Error quitting the session: {e}")
            raise