import os.path
from enum import Enum
import time

import numpy as np
import pyperclip
import selenium
import selenium.webdriver.firefox.options
import logging

from app.core.image import preprocess_image
from app.core.svg import svg_to_action

logger = logging.getLogger(__name__)

cookies_button_1 = "/html/body/div[1]/div[1]/div[2]/span[1]/a"
cookies_button_2 = '/html/body/div[2]/div[2]/div[1]/div[2]/div[2]/button[1]'
name_field = '/html/body/div/div[2]/div/div/div[4]/div[1]/div[1]/div[2]/section/span/input'

skip_adds_button = '/html/body/div[1]/div[3]/div[1]/div[2]/button'

login_button = '/html/body/div/div[2]/div/div/div[4]/div[1]/div[2]/button'
start_game = '/html/body/div/div[2]/div/div/div[2]/div[2]/span/button'
start_with_less_then_four_players = '/html/body/div/div[3]/div/span/button[1]'
draw_canvas = '/html/body/div/div[2]/div/div/div[4]/div[1]/div[2]/div/canvas[1]'
draw_canvas_2 = '/html/body/div/div[2]/div/div/div[4]/div[1]/div[2]/div/canvas[2]'
draw_canvas_3 = '/html/body/div/div[2]/div/div/div[4]/div[1]/div[2]/div/canvas[3]'
brush_tiny = '/html/body/div/div[2]/div/div/div[4]/div[2]/div/div[1]/div[1]'
brush_small = '/html/body/div/div[2]/div/div/div[4]/div[2]/div/div[1]/div[2]'
brush_medium = '/html/body/div/div[2]/div/div/div[4]/div[2]/div/div[1]/div[3]'
brush_large = '/html/body/div/div[2]/div/div/div[4]/div[2]/div/div[1]/div[4]'
brush_extra_large = '/html/body/div/div[2]/div/div/div[4]/div[2]/div/div[1]/div[5]'
invite_button = '/html/body/div/div[2]/div/div/div[2]/div[2]/span/section/button'
finish_button = '/html/body/div/div[2]/div/div/div[3]/div[2]/button'
mute_sound_button = '/html/body/div/div[2]/div/div/button'


class GameState(Enum):
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
    MASTER_WORK = 6
    STORY = 7
    MISSING_PIECE = 8
    COOP = 9
    SCORE = 10
    SANDWICH = 11
    CROWD = 12
    BACKGROUND = 13
    SOLO = 14


GAME_MODES = {
    GameMode.NORMAL: '/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[1]',
    GameMode.IMITATION: '/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[2]',
    GameMode.SECRET: '/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[3]',
    GameMode.ANIMATION: '/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[4]',
    GameMode.ICEBREAKER: '/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[5]',
    GameMode.COMPLEMENT: '/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[6]',
    GameMode.MASTER_WORK: '/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[7]',
    GameMode.STORY: '/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[8]',
    GameMode.MISSING_PIECE: '/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[9]',
    GameMode.COOP: '/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[10]',
    GameMode.SCORE: '/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[11]',
    GameMode.SANDWICH: '/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[12]',
    GameMode.CROWD: '/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[13]',
    GameMode.BACKGROUND: '/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[14]',
    GameMode.SOLO: '/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[15]'
}


class Bot:

    def __init__(self, options: selenium.webdriver.firefox.options.Options, images_dir: str = "app/data/images/"):
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
        if self.state == GameState.LOGIN_SCREEN:
            self.driver.implicitly_wait(5)
            input_field = self.driver.find_element("xpath", name_field)

            input_field.click()
            input_field.send_keys(name)
            login = self.driver.find_element("xpath", login_button)
            login.click()
            logger.info(f"logged in as {name}")
            time.sleep(5)
        else:
            logger.warning("bot is currently not in the login screen")
        self.skip_adds()

        invite = self.driver.find_element("xpath", invite_button)
        invite.click()
        print(pyperclip.paste())

    def skip_adds(self) -> None:
        """
        Skip the adds that appear on the login Screen
        """
        time.sleep(10)
        try:
            skip = self.driver.find_element("xpath", skip_adds_button)
            skip.click()
        except selenium.common.exceptions.NoSuchElementException:
            logger.info("No adds to skip")
            time.sleep(30)
        finally:
            logger.info("adds skipped")

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
        if self.state == GameState.LOBBY:
            if m := GAME_MODES.get(mode):
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
        if self.state == GameState.DRAWING:
            canvas = self.driver.find_element("xpath", draw_canvas)
            width, height = int(canvas.get_attribute("clientWidth")), int(canvas.get_property("clientHeight"))
            logger.info(f"canvas size: {width}x{height}")
            b = self.driver.find_element("xpath", brush_tiny)
            b.click()
            action = selenium.webdriver.ActionChains(self.driver)
            action.move_to_element(canvas)
            action.move_by_offset(-(width // 2) + 15, -(height // 2) + 15)
            current_x, current_y = 0, 0
            preprocess_image(image, width, height, file_name=name, tmp_file_location=self.images_dir)
            svg_to_action(action, current_x, current_y)
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

    def start_game(self) -> bool:
        """
        Starts the selected game mode if the bot is in the lobby and the owner

        :return: -> bool
        """
        if self.state == GameState.LOBBY:
            start_the_game = self.driver.find_element('xpath', start_game)
            start_the_game.click()
            try:
                button = self.driver.find_element('xpath', start_with_less_then_four_players)
                button.click()
            except selenium.common.exceptions.NoSuchElementException:
                pass
            logger.info("Starting the game")
            time.sleep(3.5)
            return True
        else:
            logger.warning("cant start the game bot is currently not in a lobby")
            return False

    def finish_drawing(self):
        pass

    def join_lobby(self, url: str) -> None:
        pass

    def interpret_image(self):
        pass

    def gen_image_from_text(self, text):
        pass

    @property
    def state(self) -> GameState:
        """
        Returns the current state of the GarticPhone Website

        :return: the current state
        """
        current_url = self.driver.current_url
        end_of_url = current_url.split('/')[-1].split('?')[0]
        if end_of_url == 'lobby':
            return GameState.LOBBY
        elif end_of_url == 'book':
            return GameState.WATCH_DRAWINGS
        elif end_of_url == 'start':
            return GameState.WRITING
        elif end_of_url == 'draw':
            return GameState.DRAWING
        elif end_of_url == 'write':
            return GameState.INTERPRETING
        else:
            return GameState.LOGIN_SCREEN
