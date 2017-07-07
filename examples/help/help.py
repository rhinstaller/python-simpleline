#!/bin/python3

from simpleline.base import App
from simpleline.render.adv_widgets import HelpScreen


if __name__ == "__main__":
    App.initialize()
    s = HelpScreen("./help/example_help.txt")
    App.get_scheduler().schedule_screen(s)
    App.run()
