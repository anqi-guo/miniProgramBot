import time

import easyocr
import requests
from selenium.common import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from BaseAutomation import BaseAutomation


class VerificationHandler(BaseAutomation):
    def __init__(self, driver, headers):
        super().__init__(driver)
        self.reader = easyocr.Reader(["en"])
        self.headers = headers
        self.first_send = True

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
                    continue  # restart loop for the refresh
                except NoSuchElementException:
                    pass  # no broken image found, proceed to the next step

                # step 3: wait for the unbroken image to load and get the url
                self.wait_for_element("//div[contains(@class, 'van-field')]//div//img")
                image_url = self.driver.find_element(By.XPATH,
                                                     "//div[contains(@class, 'van-field')]//div//img").get_attribute(
                    'src')
                if not image_url:
                    self.refresh_image()
                    continue

                # step 4: download the image
                response = requests.get(image_url, headers=self.headers, stream=True)
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
                    self.send_keys_to_element(xpath='//*[@placeholder="请输入"]', keys=code[-4:])
                    break
                else:  # fail to identify 4 digits
                    # print("识别少于4位数")
                    self.refresh_image()
                    continue
            except Exception as e:
                print(f"Error during verification code process: {e}")
                raise

    def send_keys_to_element(self, xpath, keys):
        """Send keys to an input field."""
        input_area = self.driver.find_element(By.XPATH, xpath)
        if self.first_send:
            self.first_send = False
        else:
            input_area.send_keys(Keys.COMMAND + "a")
            input_area.send_keys(Keys.DELETE)
        input_area.send_keys(keys[-4:])

    def refresh_image(self):
        self.click_element("//div[contains(@class, 'van-field')]//div//img")