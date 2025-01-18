from BaseAutomation import BaseAutomation
import time
from selenium.webdriver.common.by import By


class Homepage(BaseAutomation):
    def __init__(self, driver):
        super().__init__(driver)

    def outpatient_registration(self):
        # 弹窗：同意
        try:
            self.click_element('//android.widget.Button[@text=" 同意 "]')
        except Exception:
            pass
        try:
            self.driver.switch_to.context('WEBVIEW_com.tencent.mm:appbrand0') # 有时候要切换到appbrand2
            if not self.switch_window("index"):
                self.driver.switch_to.context('WEBVIEW_com.tencent.mm:appbrand2')
                self.switch_window("index")
            self.click_element("//wx-view[@class='title' and text()='门诊挂号']")
        except Exception as e:
            print(f"Error on homepage: {e}")
            raise