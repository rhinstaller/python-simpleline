#!/bin/python3

from simpleline.base import App
from simpleline.render.screen import UIScreen
from simpleline.render.widgets import TextWidget


class HelloWorld(UIScreen):
    title = u"Hello World"  # title is printed if there is nothing else

    def refresh(self, args=None):
        self._window = [TextWidget("Hello World")]
        return True


if __name__ == "__main__":
    App.initialize()
    screen = HelloWorld()
    App.renderer().schedule_screen(screen)
    App.run()
