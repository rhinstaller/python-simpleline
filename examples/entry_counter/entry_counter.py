#!/bin/python3

from simpleline.base import App
from simpleline.render import INPUT_PROCESSED
from simpleline.render.screen import UIScreen
from simpleline.render.widgets import TextWidget, CenterWidget


class Hub(UIScreen):
    title = u"Hub for entry counter"

    def __init__(self):
        super().__init__()
        self._counter_spoke = CounterScreen()

    def refresh(self, args=None):
        super().refresh(args)

        w = CenterWidget(TextWidget("Press '1' to enter Entry counter"))

        self.window += [w, ""]

    def input(self, args, key):
        """Run spokes based on the user choice"""
        if key == "1":
            App.renderer().switch_screen(self._counter_spoke)
            return INPUT_PROCESSED
        else:
            return key

    def prompt(self, args=None):
        """Add information to prompt for user"""
        prompt = super().prompt(args)
        prompt.add_option("1", "to enter counter spoke")
        return prompt


class CounterScreen(UIScreen):
    title = u"Counter Screen"

    def __init__(self):
        super().__init__()
        self._counter = 0

    def closed(self):
        self.ready = False

    def setup(self, args=None):
        super().setup(args)
        self._counter += 1
        return True

    def refresh(self, args=None):
        """Write message to user"""
        super().refresh(args)
        w = TextWidget("Counter {}".format(self._counter))
        self.window += [CenterWidget(w), ""]

    @property
    def counter(self):
        return self._counter


if __name__ == "__main__":
    App.initialize()
    hub = Hub()
    App.renderer().schedule_screen(hub)
    App.run()
