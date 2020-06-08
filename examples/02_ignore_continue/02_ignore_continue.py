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

# How to block the input from a user.
#
# This can be used for example to force a user to set all the required values.
# Application quit callback is also used here.
#

from simpleline import App
from simpleline.render.prompt import Prompt
from simpleline.render.screen import UIScreen, InputState
from simpleline.render.screen_handler import ScreenHandler
from simpleline.render.widgets import TextWidget, CenterWidget


def application_quit_cb(args):
    """Call this callback when the application is quitting."""
    print("Application is closing. Bye!")


class InfiniteScreen(UIScreen):

    def __init__(self):
        # We are using title as message here. Any text could be passed to the title.
        super().__init__("You need to use 'q' to quit")
        self.continue_count = 0

    def refresh(self, args=None):
        """Print text to user with number of continue clicked."""
        super().refresh(args)
        # Print counter to the screen.
        widget = TextWidget("You pressed {} times on continue".format(self.continue_count))
        # Center this counter to middle of the screen.
        center_widget = CenterWidget(widget)
        # Add the centered widget to the window container.
        self.window.add(center_widget)

    def input(self, args, key):
        """Catch 'c' keys for continue and increase counter."""
        if key == Prompt.CONTINUE:
            self.continue_count += 1
            # Do not process 'c' continue anymore.
            # This will refresh screen to refresh counter number
            return InputState.PROCESSED_AND_REDRAW

        # Process other input e.g.: 'r' refresh and 'q' quit.
        return key


if __name__ == "__main__":
    App.initialize()
    screen = InfiniteScreen()

    # Get event loop from application.
    loop = App.get_event_loop()
    # Set quit callback to the loop. When the loop quits this callback will be triggered.
    loop.set_quit_callback(application_quit_cb)

    ScreenHandler.schedule_screen(screen)
    App.run()
