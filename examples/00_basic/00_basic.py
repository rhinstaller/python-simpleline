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

# Basic usage of Simpleline.
#
# Only show screen with header and text in it.
#

from simpleline import App
from simpleline.render.screen import UIScreen
from simpleline.render.screen_handler import ScreenHandler
from simpleline.render.widgets import TextWidget


# UIScreen is the main building item for Simpleline. Every screen
# which will user see should be inherited from UIScreen.
class HelloWorld(UIScreen):

    def __init__(self):
        # Set title of the screen.
        super().__init__(title=u"Hello World")

    def refresh(self, args=None):
        # Fill the self.window attribute by the WindowContainer and set screen title as header.
        super().refresh()
        widget = TextWidget("Body text")
        self.window.add_with_separator(widget)


if __name__ == "__main__":
    # Initialize application (create scheduler and event loop).
    App.initialize()

    # Create our screen.
    screen = HelloWorld()

    # Schedule screen to the screen scheduler.
    # This can be called only after App.initialize().
    ScreenHandler.schedule_screen(screen)

    # Run the application. You must have some screen scheduled
    # otherwise it will end in an infinite loop.
    App.run()
