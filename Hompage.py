from BaseAutomation import BaseAutomation
import time

class Homepage(BaseAutomation):
    def __init__(self, driver):
        super().__init__(driver)

    def outpatient_registration(self):
        try:
            self.click_element("//*[@text='门诊挂号']")
            time.sleep(1)
            self.driver.switch_to.context("WEBVIEW_com.tencent.mm:appbrand0")
        except Exception as e:
            print(f"Error on homepage: {e}")
            raise