from BaseAutomation import BaseAutomation
import time
from selenium.webdriver.common.by import By


class Homepage(BaseAutomation):
    def __init__(self, driver):
        super().__init__(driver)

    def outpatient_registration(self):
        # 弹窗：同意
        try:
            self.driver.find_element(By.XPATH, '//android.widget.Button[@text=" 同意 "]').click()
        except Exception:
            pass

        try:
            self.driver.switch_to.context('WEBVIEW_com.tencent.mm:appbrand2')
            self.switch_window("index")
            self.click_element("//wx-view[@class='title' and text()='门诊挂号']")
        except Exception as e:
            print(f"Error on homepage: {e}")
            raise