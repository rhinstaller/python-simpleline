#!/bin/python3
#
# This file is part of Simpleline Text UI library.
#
# Copyright (C) 2020  Red Hat, Inc.
#
# Simpleline is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Simpleline is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Simpleline.  If not, see <https://www.gnu.org/licenses/>.
#

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
