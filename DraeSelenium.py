import time

import cv2
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from tqdm import tqdm

img = cv2.imread("img.png", cv2.IMREAD_GRAYSCALE)
img = cv2.resize(img, (175, 50), interpolation=cv2.INTER_AREA)
cv2.imshow("f", img)
cv2.waitKey(0)
cv2.destroyAllWindows()

height, width = img.shape

start = None
end = None
lines = []
for h, row in tqdm(enumerate(img)):
    for w, pixel in enumerate(row):
        if pixel < 255:
            if not start:
                start = w
            elif start:
                end = w
        elif start and end:
            lines.append((start, h, end, h))
            start, end = None, None
    lines.append((None, None, -500, -1))

driver = webdriver.Firefox()
driver.get("https://garticphone.com")
driver.implicitly_wait(2)
start_button = driver.find_element("xpath", '/html/body/div/div[2]/div/div/div[3]/div[1]/div[2]/button')
# name_field = driver.find_element("xpath", '/html/body/div/div[2]/div/div/div[3]/div[1]/div[1]/div[2]/section/span/input')
# name_field.sed_keys("Troll")
start_button.click()
options = driver.find_element("xpath", '/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[1]/span[2]')
options.click()

driver.find_element('xpath',
                    '/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[1]/section/label/select/option[7]').click()
driver.find_element('xpath',
                    '/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[2]/section/label/select/option[3]').click()
time.sleep(2)
start_the_game = driver.find_element('xpath', '/html/body/div/div[2]/div/div/div[2]/div[2]/span/button')
start_the_game.click()
start_with_less_then_four_players = driver.find_element('xpath', '/html/body/div/div[3]/div/span/button[1]')
start_with_less_then_four_players.click()
time.sleep(3.5)
daw_board: WebElement = driver.find_element('xpath', '/html/body/div/div[2]/div/div/div[3]/div[1]/div[2]')
canvas: WebElement = driver.find_element("xpath", '/html/body/div/div[2]/div/div/div[3]/div[1]/div[2]/div/canvas[1]')
brush = driver.find_element("xpath", '/html/body/div/div[2]/div/div/div[3]/div[2]/div/div[1]/div[2]')
brush.click()
action = ActionChains(driver)
action.move_to_element(canvas)
# width, height = int(canvas.get_attribute("width")), int(canvas.get_property("height"))
# print(width // 2, height // 2)
action.move_by_offset(-220, -110)  # move mouse to 0, 0 of the canves
current_height, current_width = 0, 0
new_line = False
for line in lines:
    x_1, y_1, x_2, y_2 = line
    if x_1 and y_1:
        x_off = x_1 - current_width
        y_off = 0 if not new_line else 3
        current_width += x_off
        action.move_by_offset(x_off, y_off)
        action.click_and_hold()
        x_off = x_2 - current_width
        y_off = 0
        current_width += x_off
        action.move_by_offset(x_off, y_off)
        action.release()
        new_line = False
    else:
        x_off = -current_width
        current_height = current_height + 1
        new_line = True

action.perform()
