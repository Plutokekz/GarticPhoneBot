from enum import Enum
import time

import cv2
from selenium import webdriver
import logging
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from tqdm import tqdm

logger = logging.getLogger(__name__)

cookies_button_1 = "/html/body/div[1]/div[1]/div[2]/span[1]/a"
cookies_button_2 = '/html/body/div[2]/div[2]/div[1]/div[2]/div[2]/button[1]'
name_field = '/html/body/div/div[2]/div/div/div[4]/div[1]/div[1]/div[2]/section/span/input'
login_button = '/html/body/div/div[2]/div/div/div[4]/div[1]/div[2]/button'
start_game = '/html/body/div/div[2]/div/div/div[2]/div[2]/span/button'
start_with_less_then_four_players = '/html/body/div/div[3]/div/span/button[1]'
draw_canvas = '/html/body/div/div[2]/div/div/div[3]/div[1]/div[2]/div/canvas[1]'
brush = '/html/body/div/div[2]/div/div/div[3]/div[2]/div/div[1]/div[1]'

class BotState(Enum):
    LOGIN_SCREEN = 0
    LOBBY = 1
    DRAWING = 2
    INTERPRETING = 3
    WRITING = 4
    WATCH_DRAWINGS = 5


class GameMode(Enum):
    NORMAL = 0
    IMITATION = 1
    SECRET = 2
    ANIMATION = 3
    ICEBREAKER = 4
    COMPLEMENT = 5
    SCORE = 6
    SPEEDRUN = 7
    SANDWICH = 8
    CROWD = 9
    BACKGROUND = 10
    SOLO = 11


GAMEMODES = {
    GameMode.NORMAL: '/html/body/div[2]/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[1]',
    GameMode.IMITATION: '/html/body/div[2]/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[2]',
    GameMode.SECRET: '/html/body/div[2]/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[3]',
    GameMode.ANIMATION: '/html/body/div[2]/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[4]',
    GameMode.ICEBREAKER: '/html/body/div[2]/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[5]',
    GameMode.COMPLEMENT: '/html/body/div[2]/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[6]',
    GameMode.SCORE: '/html/body/div[2]/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[7]',
    GameMode.SPEEDRUN: '/html/body/div[2]/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[8]',
    GameMode.SANDWICH: '/html/body/div[2]/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[9]',
    GameMode.CROWD: '/html/body/div[2]/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[10]',
    GameMode.BACKGROUND: '/html/body/div[2]/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[11]',
    GameMode.SOLO: '/html/body/div[2]/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[12]'
}


class Bot:

    def __init__(self):
        self.driver = webdriver.Firefox()

    def login(self, name: str):
        if self.state == BotState.LOGIN_SCREEN:
            input_field = self.driver.find_element("xpath", name_field)
            input_field.click()
            input_field.send_keys(name)
            login = self.driver.find_element("xpath", login_button)
            login.click()
            logger.info(f"logged in as {name}")
        else:
            logger.warning("bot is currently not in the login screen")
        time.sleep(5)

    def accept_cookies(self):
        try:
            accept_button = self.driver.find_element("xpath", cookies_button_1)
            accept_button.click()
        except NoSuchElementException:
            try:
                accept_button = self.driver.find_element("xpath", cookies_button_2)
                accept_button.click()
            except NoSuchElementException:
                logger.info("No Cookie accept button found")
        finally:
            logger.info("cookies accepted")

    def select_mode(self, mode):
        if self.state == BotState.LOBBY:
            if m := GAMEMODES.get(mode):
                m = self.driver.find_element("xpath", m)
                m.click()
                logger.info(f"selected game mode: {mode}")
                return True
            logger.warning(f"mode not found: {mode}")
            return False
        logger.warning("bot is currently not in a lobby cant select a game mode")
        return False

    # TODO add canyedge detection to draw easy shapes
    def process_image(self, image):
        img = cv2.resize(image, (175, 50), interpolation=cv2.INTER_AREA)
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
        return lines

    # TODO: add support for every photo
    def draw_image(self, image):
        if self.state == BotState.DRAWING:
            lines = self.process_image(image)
            b = self.driver.find_element("xpath", brush)
            b.click()
            canvas = self.driver.find_element("xpath", draw_canvas)
            action = ActionChains(self.driver)
            action.move_to_element(canvas)
            action.move_by_offset(-220, -110)  # move mouse to 0, 0 of the canves
            current_height, current_width = 0, 0
            new_line = False
            for line in lines:
                x_1, y_1, x_2, y_2 = line
                if x_1 and y_1:
                    x_off = x_1 - current_width
                    y_off = 0 if not new_line else 2
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
                    current_height = current_height + 1
                    new_line = True
            action.perform()

    def create_lobby(self, gartic_url='https://garticphone.com/'):
        self.driver.get(gartic_url)
        time.sleep(0.5)
        self.accept_cookies()
        # TODO: get the invite url

    def start_game(self):
        if self.state == BotState.LOBBY:
            start_the_game = self.driver.find_element('xpath', start_game)
            start_the_game.click()
            try:
                button = self.driver.find_element('xpath', start_with_less_then_four_players)
                button.click()
            except NoSuchElementException:
                pass
            logger.info("Starting the game")
            time.sleep(3.5)
        else:
            logger.warning("cant start the game bot is currently not in a lobby")

    def interpret_image(self):
        pass

    def gen_image_from_text(self, text):
        pass

    @property
    def state(self):
        current_url = self.driver.current_url
        end_of_url = current_url.split('/')[-1].split('?')[0]
        if end_of_url == 'lobby':
            return BotState.LOBBY
        elif end_of_url == 'book':
            return BotState.WATCH_DRAWINGS
        elif end_of_url == 'start':
            return BotState.WRITING
        elif end_of_url == 'draw':
            return BotState.DRAWING
        elif end_of_url == 'write':
            return BotState.INTERPRETING
        else:
            return BotState.LOGIN_SCREEN


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    bot = Bot()
    bot.create_lobby()
    bot.login("Plutokekz")
    bot.select_mode(GameMode.SOLO)
    bot.start_game()
    img = cv2.imread("img.png", cv2.IMREAD_GRAYSCALE)
    bot.draw_image(img)
    while True:
        try:
            time.sleep(10)
            print(bot.state)
        except Exception as e:
            print(e)
            break
