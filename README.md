# GarticPhoneBot
Drawing like a Human from this
![](https://github.com/Plutokekz/GarticPhoneBot/blob/master/data/images/jpg_png/YiDiplom.png?raw=true)
to this
![](https://github.com/Plutokekz/GarticPhoneBot/blob/master/data/images/jpg_png/drawing.png?raw=true)
## Installation
Clone the repository and install the requirements
```
git clone https://github.com/Plutokekz/GarticPhoneBot.git
cd GarticPhone
pip install -r requirements.txt
```
For Selenium you need 
[Mozilla Firefox](https://www.mozilla.org/de/firefox/new/) and the
[geckodriver](https://github.com/mozilla/geckodriver/releases). (Alternative you can use one of the other Selenium Driver
and the respective browser. But you have the Change the used Selenium Driver in ``Bot.py``)
Put the driver in the Project directory or in your Path.
To make an image to an SVG you need [Potrace](http://potrace.sourceforge.net/#downloading).
Put it in the Project directory or in your Path.
## Usage
Currently, you have to run ``Bot.py`` which starts Firefox and opens GarticPhone. Then it accepts the cookies and logs
itself in. After that, it selects the solo game mode and start's it. After processing the image it starts drawing.
When its finished, it will take a Screenshot of the Browser and run forever in a loop printing the current status of
the Bot.

ATTENTION

If you run ``SVGParser.py`` the svg called `processed_image` gets drawn with pyautogui. Which means it gets drawn with 
your Mouse. And the is no shortcut to interrupt it. You can only stop it by triggering the pyautogui failsafe. Therefor
the mouse has to go out of Screen. On Windows you can do this by Pressing `STRG+ALT+ENTF`.
## Documentation
Only in the code available, every function got there docstring with a little explanation