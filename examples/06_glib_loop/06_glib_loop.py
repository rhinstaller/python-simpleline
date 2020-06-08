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

# Use glib event loop instead of the original Simpleline loop.
#
# You need to have the python3-gobject installed.
#
# You can install it on Fedora by running:
#
# dnf install python3-gobject-base
#
#
# This is basic example using Glib event loop.
# You can implement your own loop abstraction. See simpleline/event_loop/glib_event_loop.
#

from simpleline import App
from simpleline.event_loop.glib_event_loop import GLibEventLoop
from simpleline.render.screen import UIScreen
from simpleline.render.screen_handler import ScreenHandler
from simpleline.render.widgets import TextWidget


class HelloWorld(UIScreen):

    def __init__(self):
        super().__init__(title=u"Hello World with GLib")

    def refresh(self, args=None):
        super().refresh()
        self.window.add_with_separator(TextWidget("Body text"))


if __name__ == "__main__":
    # Create Glib event loop.
    glib_loop = GLibEventLoop()
    # Use glib event loop instead of the original one.
    # Everything else should behave the same as with the original Simpleline loop.
    App.initialize(event_loop=glib_loop)

    screen = HelloWorld()
    ScreenHandler.schedule_screen(screen)

    # Run the application.
    App.run()
