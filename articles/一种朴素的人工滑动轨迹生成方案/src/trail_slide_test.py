# Name: 轨迹滑动测试 
# Date: 2023-09-16
# Author: Ais
# Desc: 在selenium中测试人工轨迹样本


import cv2
import time
import base64
import numpy as np

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from artificial_trail_samples import ArtificialTrailSamples


# 导入轨迹样本库
ats = ArtificialTrailSamples().load()

# 构建selenium driver
driver = webdriver.Chrome()

# 打开目标测试页面
driver.get("https://aq.jd.com/process/findPwd?s=1")

# 触发验证码 #
time.sleep(1)
WebDriverWait(driver, 3).until(
    EC.presence_of_element_located((By.XPATH, '//input[@type="text"]'))
).send_keys("+8612345678912")
time.sleep(1)
driver.find_element(By.XPATH, '//button[@type="button"]').click()

# 识别器
def recognizer():
    # ---------- 获取验证码图像 ---------- #
    # 获取背景图
    bg_img_origin_data = driver.find_element(By.XPATH, '//div[@class="JDJRV-bigimg"]/img').get_attribute("src").split(",")[1]
    bg_img_array = np.frombuffer(base64.b64decode(bg_img_origin_data), np.uint8)
    bg = cv2.imdecode(bg_img_array, cv2.COLOR_BGR2GRAY)
    # 获取缺口图
    patch_img_origin_data = driver.find_element(By.XPATH, '//div[@class="JDJRV-smallimg"]/img').get_attribute("src").split(",")[1]
    patch_img_array = np.frombuffer(base64.b64decode(patch_img_origin_data), np.uint8)
    patch = cv2.imdecode(patch_img_array, cv2.COLOR_BGR2GRAY)
    # ---------- 计算缺口偏移量 ---------- #
    # 模板匹配算法
    pos = cv2.matchTemplate(patch, bg, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(pos)
    offset = min_loc[0]
    # ---------- 构建人工轨迹并滑动 ---------- #
    ats.build(offset).slider(
        driver = driver,
        slider_xpath = '//div[@class="JDJRV-slide-inner JDJRV-slide-btn"]'  
    )
    
while True:
    try:
        time.sleep(3)
        recognizer()
    except: 
        import traceback
        print(traceback.format_exc())
    input("continue")
