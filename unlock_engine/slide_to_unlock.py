import time
from io import BytesIO
from typing import List, Optional

from PIL import Image
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

class SlideToUnlockFailed(BaseException):
    """滑动验证失败"""
    pass


class SlideToUnlockV1:
    """

    滑动验证基类
    通过缺口处有白边特性进行的识别

    """

    def __init__(self, web_driver: WebDriver):
        self.web_driver = web_driver
        self._length: int = 0
        self._image: Optional[Image] = None

    def capture_captcha_image(self, by: By, value: str) -> None:
        """ 获取验证图片
        """
        captcha_image_element = self.web_driver.find_element(by, value)
        png = captcha_image_element.screenshot_as_png
        self._image = Image.open(BytesIO(png))

    def get_sliding_distance(self) -> None:
        """
        得到滑动距离
        通过缺口处有白边特性进行的识别
        """

        # 灰度处理
        gray_png = self._image.convert('L')

        # 二值化
        threshold = 240
        table = [0 if i < threshold else 1 for i in range(256)]
        bin_png = gray_png.point(table, '1')

        # 将每个像素点 黑的为 0、白的为 1 存放进二维列表
        png_dict = []
        for x in range(bin_png.size[0]):
            png_dict.append([bin_png.getpixel((x, y)) for y in range(bin_png.size[1])])

        # 找出 x 轴白色像素点大于 40 个的 x 值
        gt_40_x = [index for index, line in enumerate(png_dict) if sum(line) >= 40 and index > 61]
        self._length = min(gt_40_x)

    @staticmethod
    def get_forward_tracks(length: int) -> List[int]:
        """ 模拟滑动的轨迹
        """
        # 移动轨迹
        track = []
        # 减速阈值
        mid = length * 3 / 5
        # 计算间隔
        t = 0.2
        # 初速度
        v = 0
        # 滑超过过一段距离
        length += 15
        while sum(track) < length:
            if sum(track) < mid:
                # 加速度为正
                a = 1
            else:
                # 加速度为负
                a = -0.5
            # 初速度 v0
            v0 = v
            # 当前速度 v
            v = v0 + a * t
            # 移动距离 v0t + 1/2*a*t*t
            move = v0 * t + 1 / 2 * a * t * t
            track.append(round(move))
        return track

    def move_sliding_block(self, by: By, value: str) -> None:
        """ 默认人移动滑块
        """
        element = self.web_driver.find_element(by, value)
        action = ActionChains(self.web_driver, duration=6)

        # 左键按住不放
        action.click_and_hold(element).perform()
        time.sleep(0.2)

        # 得到向前向后的轨迹
        forward_tracks = self.get_forward_tracks(self._length)
        back_tracks = [-1, -1, -2, -2, -3, -2, -2, -1, -1]

        # 正向移动滑块
        for x in forward_tracks:
            action.move_by_offset(xoffset=x, yoffset=0).perform()

        time.sleep(0.1)
        # 逆向移动滑块
        for x in back_tracks:
            action.move_by_offset(xoffset=x, yoffset=0).perform()

        # 模拟抖动
        action.move_by_offset(xoffset=-2, yoffset=0).perform()
        action.move_by_offset(xoffset=2, yoffset=0).perform()

        # 松开左键
        action.release().perform()

    def slide_to_unlock(self, img_element: tuple[By, str], sliding_block_element: tuple[By, str], is_success_element: tuple[By, str], retry_count: int = 3):
        """
        主要程序入口
        弹出滑动解锁弹窗后执行

        img_element 滑动图片element: tuple[By, str] 例 (By.ID, 'cpc_img')
        sliding_block_element 滑块element: tuple[By, str] 例 (By.XPATH, '//div[@class="sp_msg"]/img')
        is_success_element tuple[By, str] 滑动解锁成功才出现的element 例 (By.XPATH, '//button[@class="getMsg-btn text-btn J_ping"]')
        retry_count 重试次数 默认 3
        """
        for _ in range(retry_count):
            # 得到图片
            self.capture_captcha_image(*img_element)

            # 得到滑动长度
            self.get_sliding_distance()

            # 模拟滑动
            self.move_sliding_block(*sliding_block_element)
            time.sleep(3)

            # 判断是否成功
            if self.web_driver.find_element(*is_success_element):
                return

        raise SlideToUnlockFailed