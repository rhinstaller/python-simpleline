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

# Simple divider screen.
#
# User input processing example.
#
#

import re

from simpleline import App
from simpleline.render.screen import UIScreen, InputState
from simpleline.render.screen_handler import ScreenHandler
from simpleline.render.widgets import TextWidget


class DividerScreen(UIScreen):

    def __init__(self):
        # Set title of the screen.
        super().__init__(title=u"Divider")
        self._message = 0

    def refresh(self, args=None):
        # Fill the self.window attribute by the WindowContainer and set screen title as header.
        super().refresh()

        widget = TextWidget("Result: " + str(self._message))
        self.window.add_with_separator(widget)

    def prompt(self, args=None):
        # Change user prompt
        prompt = super().prompt()

        # Set message to the user prompt. Give a user hint how he/she may control our application.
        prompt.set_message("Pass numbers to divider in a format: 'num / num'")

        # Remove continue option from the control. There is no need for that
        # when we have only one screen.
        prompt.remove_option('c')

        return prompt

    def input(self, args, key):
        """Process input from user and catch numbers with '/' symbol."""

        # Test if user passed valid input for divider.
        # This will basically take number + number and nothing else and only positive numbers.
        groups = re.match(r'(\d+) *\/ *(\d+)$', key)
        if groups:
            num1 = int(groups[1])
            num2 = int(groups[2])

            # Dividing by zero is not valid so we won't accept this input from the user. New
            # input is then required from the user.
            if num2 == 0:
                return InputState.DISCARDED

            self._message = int(num1 / num2)

            # Because this input is processed we need to show this screen (show the result).
            # This will call refresh so our new result will be processed inside of the refresh()
            # method.
            return InputState.PROCESSED_AND_REDRAW

        # Not input for our screen, try other default inputs. This will result in the
        # same state as DISCARDED when no default option is used.
        return key


if __name__ == "__main__":
    # Initialize application (create scheduler and event loop).
    App.initialize()

    # Create our screen.
    screen = DividerScreen()

    # Schedule screen to the screen scheduler.
    # This can be called only after App.initialize().
    ScreenHandler.schedule_screen(screen)

    # Run the application. You must have some screen scheduled
    # otherwise it will end in an infinite loop.
    App.run()
