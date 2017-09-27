#!/bin/python3
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
