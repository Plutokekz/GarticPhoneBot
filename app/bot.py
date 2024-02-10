import logging
import time

import cv2
import selenium

from app.core.api import Bot, GameMode


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
    while not bot.start_game():
        pass
    img = cv2.imread("app/data/images/jpg_png/img.png")
    bot.draw_image(img, "processed_image")
    while True:
        try:
            time.sleep(10)
    #        print(bot.state)
        except Exception as e:
            print(e)
            break


if __name__ == "__main__":
    main()
