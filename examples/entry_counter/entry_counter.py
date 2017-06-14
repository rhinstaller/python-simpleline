#!/bin/python3

from simpleline import INPUT_PROCESSED
from simpleline.base import UIScreen, App
from simpleline.render.widgets import TextWidget, CenterWidget


class Hub(UIScreen):
    title = u"Hub for entry counter"

    def __init__(self, app):
        super().__init__(app)
        self._counter_spoke = CounterScreen(app)

    def refresh(self, args=None):
        super().refresh(args)

        w = CenterWidget(TextWidget("Press '1' to enter Entry counter"))

        self._window += [w, ""]
        return True

    def input(self, args, key):
        """Run spokes based on the user choice"""
        if key == "1":
            self.app.switch_screen_with_return(self._counter_spoke)
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

    def __init__(self, app):
        super().__init__(app)
        self._counter = 0

    def closed(self):
        self._ready = False

    def setup(self, args=None):
        super().setup(args)
        self._counter += 1

    def refresh(self, args=None):
        """Write message to user"""
        super().refresh(args)
        w = TextWidget("Counter {}".format(self._counter))
        self._window += [CenterWidget(w), ""]
        return True

    @property
    def counter(self):
        return self._counter


if __name__ == "__main__":
    a = App("Hubs and Spokes")
    s = Hub(a)
    a.schedule_screen(s)
    a.run()
