#!/bin/python3
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
            # Redraw this screen again. This is required because the processing is stopped
            # without a new screen pushed. Without this redraw call the application will stay in
            # an infinite loop.
            # This will add the event to the event loop for later processing.
            self.redraw()
            # Do not process 'c' continue anymore.
            return InputState.PROCESSED

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
