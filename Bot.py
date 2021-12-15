from enum import Enum
import time
from selenium import webdriver

cookies_button_1 = "/html/body/div[1]/div[1]/div[2]/span[1]/a"

class BotState(Enum):
    LOGIN_SCREEN = 0
    LOBBY = 1
    DRAWING = 2
    INTERPRETING = 3
    WRITING = 4
    WATCH_DRAWINGS = 5


class Bot:

    def __init__(self, gartic_url='https://garticphone.com/'):
        self.driver = webdriver.Firefox()
        self.driver.get(gartic_url)
        time.sleep(2)
        self.accept_cookies()

    def accept_cookies(self):
        try:
            accept_button = self.driver.find_element("xpath", '/html/body/div[2]/div[2]/div[1]/div[2]/div[2]/button[1]')
            accept_button.click()
        except Exception as e:
            print(e)

    def draw_image(self, image):
        pass

    def create_lobby(self, options):
        pass

    def interpret_image(self):
        pass

    def gen_image_from_text(self, text):
        pass

    @property
    def state(self):
        current_url = self.driver.current_url
        print(current_url.split('/')[-1])


if __name__ == "__main__":
    bot = Bot()
    while True:
        try:
            time.sleep(10)
            bot.state
        except Exception as e:
            print(e)
            break

