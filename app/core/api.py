"""
This module contains the Api for the GarticPhone Website
"""

import os.path
from enum import Enum
import time
import logging


import numpy as np
import pyperclip
import selenium
import selenium.webdriver.firefox.options

from app.core.image import preprocess_image
from app.core.svg import svg_to_action

logger = logging.getLogger(__name__)

COOKIES_BUTTON_1 = "/html/body/div[1]/div[1]/div[2]/span[1]/a"
COOKIES_BUTTON_2 = "/html/body/div[2]/div[2]/div[1]/div[2]/div[2]/button[1]"
NAME_FIELD = "/html/body/div/div[2]/div/div/div[4]/div[1]/div[1]/div[2]/section/span/input"

SKIP_ADDS_BUTTON = "/html/body/div[1]/div[3]/div[1]/div[2]/button"

LOGIN_BUTTON = "/html/body/div/div[2]/div/div/div[4]/div[1]/div[2]/button"
START_GAME = "/html/body/div/div[2]/div/div/div[2]/div[2]/span/button"
START_WITH_LESS_THEN_FOUR_PLAYERS = "/html/body/div/div[3]/div/span/button[1]"
DRAW_CANVAS = "/html/body/div/div[2]/div/div/div[4]/div[1]/div[2]/div/canvas[1]"
DRAW_CANVAS_2 = "/html/body/div/div[2]/div/div/div[4]/div[1]/div[2]/div/canvas[2]"
DRAW_CANVAS_3 = "/html/body/div/div[2]/div/div/div[4]/div[1]/div[2]/div/canvas[3]"
BRUSH_TINY = "/html/body/div/div[2]/div/div/div[4]/div[2]/div/div[1]/div[1]"
BRUSH_SMALL = "/html/body/div/div[2]/div/div/div[4]/div[2]/div/div[1]/div[2]"
BRUSH_MEDIUM = "/html/body/div/div[2]/div/div/div[4]/div[2]/div/div[1]/div[3]"
BRUSH_LARGE = "/html/body/div/div[2]/div/div/div[4]/div[2]/div/div[1]/div[4]"
BRUSH_EXTRA_LARGE = "/html/body/div/div[2]/div/div/div[4]/div[2]/div/div[1]/div[5]"
INVITE_BUTTON = "/html/body/div/div[2]/div/div/div[2]/div[2]/span/section/button"
FINISH_BUTTON = "/html/body/div/div[2]/div/div/div[3]/div[2]/button"
MUTE_SOUND_BUTTON = "/html/body/div/div[2]/div/div/button"


class GameState(Enum):
    """
    The current state of the GarticPhone Website
    """

    LOGIN_SCREEN = 0
    LOBBY = 1
    DRAWING = 2
    INTERPRETING = 3
    WRITING = 4
    WATCH_DRAWINGS = 5


class GameMode(Enum):
    """
    The different game modes of GarticPhone
    """

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
    GameMode.NORMAL: "/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[1]",
    GameMode.IMITATION: "/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[2]",
    GameMode.SECRET: "/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[3]",
    GameMode.ANIMATION: "/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[4]",
    GameMode.ICEBREAKER: "/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[5]",
    GameMode.COMPLEMENT: "/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[6]",
    GameMode.MASTER_WORK: "/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[7]",
    GameMode.STORY: "/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[8]",
    GameMode.MISSING_PIECE: "/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[9]",
    GameMode.COOP: "/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[10]",
    GameMode.SCORE: "/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[11]",
    GameMode.SANDWICH: "/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[12]",
    GameMode.CROWD: "/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[13]",
    GameMode.BACKGROUND: "/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[14]",
    GameMode.SOLO: "/html/body/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[15]",
}


class Bot:
    """
    The Bot for the GarticPhone Website
    """

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
            input_field = self.driver.find_element("xpath", NAME_FIELD)

            input_field.click()
            input_field.send_keys(name)
            login = self.driver.find_element("xpath", LOGIN_BUTTON)
            login.click()
            logger.info(f"logged in as {name}")
            time.sleep(5)
        else:
            logger.warning("bot is currently not in the login screen")
        self.skip_adds()

        invite = self.driver.find_element("xpath", INVITE_BUTTON)
        invite.click()
        print(pyperclip.paste())

    def skip_adds(self) -> None:
        """
        Skip the adds that appear on the login Screen
        """
        time.sleep(10)
        try:
            skip = self.driver.find_element("xpath", SKIP_ADDS_BUTTON)
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
            accept_button = self.driver.find_element("xpath", COOKIES_BUTTON_1)
            accept_button.click()
        except selenium.common.exceptions.NoSuchElementException:
            try:
                accept_button = self.driver.find_element("xpath", COOKIES_BUTTON_2)
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
                element = self.driver.find_element("xpath", m)
                element.click()
                logger.info(f"selected game mode: {mode}")
                return True
            logger.warning(f"mode not found: {mode}")
            return False
        logger.warning("bot is currently not in a lobby cant select a game mode")
        return False

    def draw_image(self, image: np.ndarray, name: str) -> None:
        """
        If the Bot ist in drawing state, you can draw the given image

        :param image: cv2 image you want to draw
        :param name: name of the svg and bmp file which get created in the process
        :return: None
        """
        if self.state == GameState.DRAWING:
            canvas = self.driver.find_element("xpath", DRAW_CANVAS)
            c_width, c_height = canvas.get_attribute("clientWidth"), canvas.get_attribute("clientHeight")
            if c_width is None:
                raise ValueError("canvas size not found")
            if c_height is None:
                raise ValueError("canvas size not found")
            width: int = int(c_width)
            height: int = int(c_height)
            logger.info(f"canvas size: {width}x{height}")
            b = self.driver.find_element("xpath", BRUSH_TINY)
            b.click()
            action = selenium.webdriver.ActionChains(self.driver)
            action.move_to_element(canvas)
            action.move_by_offset(-(width // 2) + 15, -(height // 2) + 15)
            current_x, current_y = 0, 0
            preprocess_image(image, width, height, file_name=name, tmp_file_location=self.images_dir)
            svg_to_action(action, current_x, current_y)
            action.perform()
            self.driver.save_screenshot(os.path.join(self.images_dir, "jpg_png", "drawing.png"))

    def create_lobby(self, gartic_url: str = "https://garticphone.com/en") -> None:
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
            start_the_game = self.driver.find_element("xpath", START_GAME)
            start_the_game.click()
            try:
                button = self.driver.find_element("xpath", START_WITH_LESS_THEN_FOUR_PLAYERS)
                button.click()
            except selenium.common.exceptions.NoSuchElementException:
                pass
            logger.info("Starting the game")
            time.sleep(3.5)
            return True
        logger.warning("cant start the game bot is currently not in a lobby")
        return False

    def finish_drawing(self):
        """
        Finish the drawing if the bot is currently in the drawing state
        :return:
        """

    def join_lobby(self, url: str) -> None:
        """
        Join a lobby with the given url
        :param url:
        :return:
        """

    def interpret_image(self):
        """
        Interpret the image if the bot is currently in the interpreting state
        :return:
        """

    def gen_image_from_text(self, text):
        """
        Generate an image from the given text
        :param text:
        :return:
        """

    @property
    def state(self) -> GameState:
        """
        Returns the current state of the GarticPhone Website

        :return: the current state
        """
        current_url = self.driver.current_url
        end_of_url = current_url.split("/")[-1].split("?")[0]
        if end_of_url == "lobby":
            return GameState.LOBBY
        if end_of_url == "book":
            return GameState.WATCH_DRAWINGS
        if end_of_url == "start":
            return GameState.WRITING
        if end_of_url == "draw":
            return GameState.DRAWING
        if end_of_url == "write":
            return GameState.INTERPRETING
        return GameState.LOGIN_SCREEN
