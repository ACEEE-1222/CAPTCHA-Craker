import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
import cv2 as cv
import time

# 设置 Chrome WebDriver 的选项
path = r"D:\chromedriver-win64\chromedriver.exe"
service = Service(path)
# 创建 Chrome WebDriver 的选项对象
chrome_options = Options()
# GPU硬件加速
chrome_options.add_argument('–-disable-gpu')
# 彻底停用沙箱
chrome_options.add_argument('--no-sandbox')
# 创建临时文件共享内存
chrome_options.add_argument('--disable-dev-shm-usage')
# 单进程运行
chrome_options.add_argument('-–single-process')
# 禁用window.navigator.webdriver
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
browser = webdriver.Chrome(service=service,options=chrome_options)
browser.get('https://upass.10jqka.com.cn/login')


def get_track(distance):
    """
    计算滑块移动轨迹
    :param distance: 滑块需要移动的距离
    :return: 返回移动轨迹
    """
    track = []
    current = 0
    mid = distance * 3 / 4
    t = 0.2
    v = 0
    while current < distance:
        if current < mid:
            a = 2
        else:
            a = -3
        v0 = v
        v = v0 + a * t
        move = v0 * t + 1 / 2 * a * t * t
        current += move
        track.append(round(move))
    return track


# 滑块验证
def move_verify():
    error_num = 0
    dis = 0
    while error_num <= 5:
        print('下载图片...')
        # 获取背景图片的URL
        bg_img_element = browser.find_element(By.ID, 'slicaptcha-img')
        bg_img_url = bg_img_element.get_attribute("src")
        # 获取滑块图片的URL
        cg_img_element = browser.find_element(By.ID, 'slicaptcha-block')
        cg_img_url = cg_img_element.get_attribute("src")
        # 下载图片到本地
        with open('spiders/bg.jpg', 'wb') as f:
            f.write(requests.get(bg_img_url).content)
        with open('spiders/cg.jpg', 'wb') as f:
            f.write(requests.get(cg_img_url).content)

        print('开始计算距离...')
        dis = get_distance('bg.jpg','cg.jpg')  # 如果返回为空  则需要重新获取图片
        if dis != 0:
            print(dis)
            dis = round(dis * 466 / 518, 2)-0.5  # 466和518分别是在网页上和在本地上背景图片的长，-0.5是微调
            print(f'实际距离:{dis}')
            break
        else:
            print('返回了0')
            browser.find_element(By.ID, 'slicaptcha-icon').click()  # 未识别到距离  则重新获取验证
            error_num += 1
    btn = browser.find_element(By.ID, 'slider')  # 获取滑块
    ActionChains(browser).click_and_hold(btn).perform()  # 定义滑动  调用函数缓慢滑动滑块
    for x in get_track(dis):
        ActionChains(browser).move_by_offset(xoffset=x, yoffset=0).perform()

    ActionChains(browser).release().perform()
    print('登陆成功')
    return browser.get_cookies()

def get_pos(bg_img, cg_img):
    """
    :param bg_img: 背景图片
    :param cg_img: 滑块图片
    :return int
    """

    # 识别图片边缘
    bg_edge = cv.Canny(bg_img, 100, 200)
    cg_edge = cv.Canny(cg_img, 100, 200)

    # 保存边缘检测后的图像
    cv.imwrite('background_edges.jpg', bg_edge)
    cv.imwrite('foreground_edges.jpg', cg_edge)

    # 转换图片格式
    bg_pic = cv.cvtColor(bg_edge, cv.COLOR_GRAY2RGB)
    cg_pic = cv.cvtColor(cg_edge, cv.COLOR_GRAY2RGB)

    # 缺口匹配
    res = cv.matchTemplate(bg_pic, cg_pic, cv.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)

    print(min_val, max_val, min_loc, max_loc)

    # 返回缺口的X坐标
    return max(max_loc[0],0)



def get_distance(bg_img, cg_img):
    return get_pos(cv.imread(bg_img),cv.imread(cg_img))


def get_cookies():
    time.sleep(5)
    # 切换为密码登陆
    browser.find_element(By.ID, "to_account_login").click()
    browser.find_element(By.ID, 'uname').send_keys('mx_716881787')
    browser.find_element(By.ID, 'passwd').send_keys('hzy741852963')
    time.sleep(3)
    # 点击登陆
    browser.find_element(By.XPATH, '/html/body/div[2]/div[2]/div[2]/div[4]/div[4]').click()
    time.sleep(4)
    # 破解滑块验证码
    cookies = move_verify()
    print(cookies)
    return cookies

if __name__ == '__main__':
    get_distance('bg.jpg','cg.jpg')




