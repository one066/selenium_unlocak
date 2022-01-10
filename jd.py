import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from unlock_engine.slide_to_unlock import SlideToUnlockV1, SlideToUnlockFailed


class JdService:
    """

    jd service

    """

    LOGIN_URL: str = 'https://plogin.m.jd.com/login/login'

    def __init__(self):
        self.web_driver = webdriver.Chrome(service=Service(os.path.join(os.getcwd(), 'chromedriver')))

    def login(self) -> None:
        self.web_driver.get(self.LOGIN_URL)

        # 输入 号码
        phone_input_element_xpath = '//input[@class="acc-input mobile J_ping"]'
        self.web_driver.find_element(By.XPATH, phone_input_element_xpath).send_keys('*********')
        time.sleep(1)

        # 点击获取验证码
        get_captcha_element_xpath = '//button[@class="getMsg-btn text-btn J_ping timer active"]'
        self.web_driver.find_element(By.XPATH, get_captcha_element_xpath).click()
        time.sleep(1)

        slide_to_unlock_v1 = SlideToUnlockV1(self.web_driver)
        try:
            slide_to_unlock_v1.slide_to_unlock(
                img_element=(By.ID, 'cpc_img'),
                sliding_block_element=(By.XPATH, '//div[@class="sp_msg"]/img'),
                is_success_element=(By.XPATH, '//button[@class="getMsg-btn text-btn J_ping"]'),
                retry_count=5
            )
        except SlideToUnlockFailed:
            print('解锁失败')

        time.sleep(0.5)
        self.web_driver.find_element(By.XPATH, '//input[@class="policy_tip-checkbox"]').click()

        time.sleep(0.5)
        auth_code = input('请输入收到的验证码:')
        self.web_driver.find_element(By.ID, 'authcode').send_keys(auth_code)

        time.sleep(0.5)
        self.web_driver.find_element(By.XPATH, '//a[@class="btn J_ping btn-active"]').click()

        time.sleep(3)
        print({'pt_pin': self.web_driver.get_cookie('pt_pin')['value'],
               'pt_key': self.web_driver.get_cookie('pt_key')['value']})

        # ================================= #
        #            接着进行操作             #
        # ================================= #


if __name__ == '__main__':
    jd_service = JdService()
    jd_service.login()
