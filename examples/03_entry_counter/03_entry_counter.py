#!/bin/python3

from simpleline import App
from simpleline.render.screen import UIScreen, InputState
from simpleline.render.screen_handler import ScreenHandler
from simpleline.render.widgets import TextWidget, CenterWidget


class Hub(UIScreen):

    def __init__(self):
        super().__init__("Hub for entry counter")
        self._counter_spoke = CounterScreen()

    def refresh(self, args=None):
        super().refresh(args)

        w = CenterWidget(TextWidget("Press '1' to enter Entry counter"))

        self.window.add_with_separator(w)

    def input(self, args, key):
        """Run spokes based on the user choice."""
        if key == "1":
            ScreenHandler.push_screen(self._counter_spoke)
            # this input was processed
            return InputState.PROCESSED
        else:
            # return for outer processing
            # the basic processing is 'c' for continue, 'r' for refresh, 'q' to quit
            # otherwise the input is discarded and waiting for a new input
            return key

    def prompt(self, args=None):
        """Add our information to the prompt."""
        prompt = super().prompt(args)
        prompt.add_option("1", "to enter counter spoke")
        return prompt


class CounterScreen(UIScreen):

    def __init__(self):
        super().__init__("Counter Screen")
        self._counter = 0

    def closed(self):
        super().closed()
        self.screen_ready = False

    def setup(self, args=None):
        super().setup(args)
        self._counter += 1
        return True

    def refresh(self, args=None):
        """Write message to user."""
        super().refresh(args)
        w = TextWidget("Counter {}".format(self._counter))
        self.window.add_with_separator(CenterWidget(w))

    @property
    def counter(self):
        return self._counter


if __name__ == "__main__":
    App.initialize()
    hub = Hub()
    ScreenHandler.schedule_screen(hub)
    App.run()
