import os.path
from enum import Enum
import time

import cv2
import numpy as np
import selenium
import selenium.webdriver.firefox.options
import logging
import ImageProcessor
import SVGParser

# import pyperclip

logger = logging.getLogger(__name__)

cookies_button_1 = "/html/body/div[1]/div[1]/div[2]/span[1]/a"
cookies_button_2 = '/html/body/div[2]/div[2]/div[1]/div[2]/div[2]/button[1]'
# name_field = '/html/body/div[2]/div[2]/div/div/div[3]/div[1]/div[1]/div[2]/section/span/input'#'/html/body/div/div[2]/div/div/div[4]/div[1]/div[1]/div[2]/section/span/input'
name_field = '/html/body/div/div[2]/div/div/div[4]/div[1]/div[1]/div[2]/section/span/input'
# '/html/body/div/div[2]/div/div/div[3]/div[1]/div[1]/div[2]/section/span/input'

login_button = '/html/body/div/div[2]/div/div/div[4]/div[1]/div[2]/button'
start_game = '/html/body/div/div[2]/div/div/div[2]/div[2]/span/button'
start_with_less_then_four_players = '/html/body/div/div[3]/div/span/button[1]'
draw_canvas = '/html/body/div/div[2]/div/div/div[3]/div[1]/div[2]/div/canvas[1]'
brush = '/html/body/div/div[2]/div/div/div[3]/div[2]/div/div[1]/div[1]'
invite_button = '/html/body/div/div[2]/div/div/div[2]/div[2]/span/section/button'


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
    # GameMode.SOLO: '/html/body/div[2]/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[12]'
    GameMode.SOLO: '/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[12]'
}


class Bot:

    def __init__(self, options: selenium.webdriver.firefox.options.Options, images_dir: str = "data/images/"):
        """
        Initialing the bot with the given options for the firefox selenium driver

        :param options: options for firefox (may something like headless)
        :param images_dir: the directory where the processes image should be saved
        """
        self.driver = selenium.webdriver.Firefox(options=options)
        self.images_dir = images_dir

    def login(self, name: str) -> None:
        """
        Login in with the given name
        TODO: handle timeouts with selenium so there is no need for time.sleep

        :param name: the username for GarticPhone
        :return: None
        """
        if self.state == BotState.LOGIN_SCREEN:
            self.driver.implicitly_wait(5)
            input_field = self.driver.find_element("xpath", name_field)

            input_field.click()
            input_field.send_keys(name)
            login = self.driver.find_element("xpath", login_button)
            login.click()
            logger.info(f"logged in as {name}")
            time.sleep(5)
            # invite = self.driver.find_element("xpath", invite_button)
            # invite.click()
            # return pyperclip.paste()
        else:
            logger.warning("bot is currently not in the login screen")

    def accept_cookies(self) -> None:
        """
        Accept the cookies that apper on the login Screen
        TODO: handle timeouts and if there where no cookies found

        :return: None
        """
        try:
            accept_button = self.driver.find_element("xpath", cookies_button_1)
            accept_button.click()
        except selenium.common.exceptions.NoSuchElementException:
            try:
                accept_button = self.driver.find_element("xpath", cookies_button_2)
                accept_button.click()
            except selenium.common.exceptions.NoSuchElementException:
                logger.info("No Cookie accept button found")
        finally:
            logger.info("cookies accepted")
        time.sleep(5)

    def select_mode(self, mode: GameMode) -> bool:
        """
        select a game mode if the Bot is currently in the lobby and the owner

        :param mode: the game mode you want to play, currently only Solo it compatible
        :return: boolean if the game mode got selected
        """
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

    def draw_image(self, image: np.array, name: str) -> None:
        """
        If the Bot ist in drawing state, you can draw the given image

        :param image: cv2 image you want to draw
        :param name: name of the svg and bmp file which get created in the process
        :return: None
        """
        if self.state == BotState.DRAWING:
            canvas = self.driver.find_element("xpath", draw_canvas)
            width, height = int(canvas.get_attribute("clientWidth")), int(canvas.get_property("clientHeight"))
            logger.info(f"canvas size: {width}x{height}")
            b = self.driver.find_element("xpath", brush)
            b.click()
            action = selenium.webdriver.ActionChains(self.driver)
            action.move_to_element(canvas)
            action.move_by_offset(-width // 2, -height // 2)
            current_x, current_y = 0, 0
            ImageProcessor.preprocess_image(image, width, height, file_name=name, tmp_file_location=self.images_dir)
            SVGParser.svg_to_action(action, current_x, current_y)
            action.perform()
            self.driver.save_screenshot(os.path.join(self.images_dir, "jpg_png", "drawing.png"))

    def create_lobby(self, gartic_url: str = 'https://garticphone.com/en') -> None:
        """
        Open the garticphone site and accepting the cookies, if they appear

        :param gartic_url: the url if garticphone
        :return: None
        """
        self.driver.get(gartic_url)
        time.sleep(0.5)
        self.accept_cookies()

    def start_game(self) -> None:
        """
        Starts the selected game mode if the bot is in the lobby and the owner

        :return: -> None
        """
        if self.state == BotState.LOBBY:
            start_the_game = self.driver.find_element('xpath', start_game)
            start_the_game.click()
            try:
                button = self.driver.find_element('xpath', start_with_less_then_four_players)
                button.click()
            except selenium.common.exceptions.NoSuchElementException:
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
    def state(self) -> BotState:
        """
        Returns the current state of the GarticPhone Website

        :return: the current state
        """
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


def main():
    """
    Main function to test the Bot
    :return: None
    """
    options = selenium.webdriver.firefox.options.Options()
    # options.add_argument("-headless")
    # options.binary_location = r"/opt/firefox/firefox-bin"
    logging.basicConfig(level=logging.INFO)
    bot = Bot(options)
    bot.create_lobby()
    bot.login("Plutokekz")
    bot.select_mode(GameMode.SOLO)
    bot.start_game()
    img = cv2.imread("data/images/jpg_png/YiDiplom.png")
    bot.draw_image(img, "processed_image")
    while True:
        try:
            time.sleep(10)
            print(bot.state)
        except Exception as e:
            print(e)
            break


if __name__ == "__main__":
    main()
