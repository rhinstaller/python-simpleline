#!/bin/python3

from simpleline import App
from simpleline.render.screen import UIScreen
from simpleline.render.widgets import TextWidget


class HelloWorld(UIScreen):
    title = u"Hello World"  # title is printed if there is nothing else

    def refresh(self, args=None):
        super().refresh()
        self.window.add(TextWidget("Hello World"))
        self.window.add_separator()


if __name__ == "__main__":
    App.initialize()
    screen = HelloWorld()
    App.get_scheduler().schedule_screen(screen)
    App.run()
