#!/bin/python3

from simpleline import App
from simpleline.render import InputState
from simpleline.render.screen import UIScreen
from simpleline.render.widgets import TextWidget, CenterWidget


class Hub(UIScreen):

    def __init__(self):
        super().__init__("Hub for entry counter")
        self._counter_spoke = CounterScreen()

    def refresh(self, args=None):
        super().refresh(args)

        w = CenterWidget(TextWidget("Press '1' to enter Entry counter"))

        self.window.add(w)
        self.window.add_separator()

    def input(self, args, key):
        """Run spokes based on the user choice"""
        if key == "1":
            App.get_scheduler().push_screen(self._counter_spoke)
            return InputState.PROCESSED
        else:
            return key

    def prompt(self, args=None):
        """Add information to prompt for user"""
        prompt = super().prompt(args)
        prompt.add_option("1", "to enter counter spoke")
        return prompt


class CounterScreen(UIScreen):

    def __init__(self):
        super().__init__("Counter Screen")
        self._counter = 0

    def closed(self):
        self.screen_ready = False

    def setup(self, args=None):
        super().setup(args)
        self._counter += 1
        return True

    def refresh(self, args=None):
        """Write message to user"""
        super().refresh(args)
        w = TextWidget("Counter {}".format(self._counter))
        self.window.add(CenterWidget(w), "")

    @property
    def counter(self):
        return self._counter


if __name__ == "__main__":
    App.initialize()
    hub = Hub()
    App.get_scheduler().schedule_screen(hub)
    App.run()
