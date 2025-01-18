from BaseAutomation import BaseAutomation
import time
from selenium.webdriver.common.by import By


class Homepage(BaseAutomation):
    def __init__(self, driver):
        super().__init__(driver)

    def is_open(self):
        wechat_element = self.driver.find_elements(By.XPATH, '//android.widget.TextView[@resource-id="com.tencent.mm:id/icon_tv" and @text="微信"]')
        return len(wechat_element) == 0

    def open_mini_program(self):
        window_size = self.driver.get_window_size()
        self.driver.flick(window_size['width'] * 0.5, window_size['height'] * 0.4, window_size['width'] * 0.5, window_size['height'] * 0.9)
        self.driver.find_elements(By.XPATH, '//*[@text="重医一院"]')[0].click()

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