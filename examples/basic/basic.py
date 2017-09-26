#!/bin/python3

from simpleline import App
from simpleline.render.screen import UIScreen
from simpleline.render.screen_handler import ScreenHandler
from simpleline.render.widgets import TextWidget


class HelloWorld(UIScreen):

    def __init__(self):
        super().__init__(title=u"Hello World")

    def refresh(self, args=None):
        super().refresh()
        self.window.add_with_separator(TextWidget("Body text"))


if __name__ == "__main__":
    App.initialize()
    screen = HelloWorld()
    ScreenHandler.schedule_screen(screen)
    App.run()
