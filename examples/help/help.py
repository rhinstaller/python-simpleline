#!/bin/python3

from simpleline import App
from simpleline.render.screen_handler import ScreenHandler
from simpleline.render.adv_widgets import HelpScreen


if __name__ == "__main__":
    App.initialize()
    s = HelpScreen("./help/example_help.txt")
    ScreenHandler.schedule_screen(s)
    App.run()
