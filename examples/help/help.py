#!/bin/python3

from simpleline.base import App
from simpleline.adv_widgets import HelpScreen


if __name__ == "__main__":
    a = App("Hello World")
    s = HelpScreen(a, "./help/example_help.txt")
    a.schedule_screen(s)
    a.run()
