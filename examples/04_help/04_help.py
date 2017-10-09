#!/bin/python3
#
# Show help screen.
#
# Usage of the HelpScreen advanced widget.
# There are many of advanced widgets which have different uses.
# I've recommend developer to look on them.

from simpleline import App
from simpleline.render.screen_handler import ScreenHandler
from simpleline.render.adv_widgets import HelpScreen


if __name__ == "__main__":
    App.initialize()
    # You need to pass file with help text to the screen.
    s = HelpScreen("./04_help/example_help.txt")
    ScreenHandler.schedule_screen(s)
    App.run()
