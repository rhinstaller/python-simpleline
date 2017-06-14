#!/bin/python3

from simpleline import INPUT_PROCESSED
from simpleline.base import App, UIScreen
from simpleline.render.prompt import Prompt
from simpleline.render.widgets import TextWidget, CenterWidget


class MyApp(App):
    def application_quit_cb(self):
        print("Application is closing. Bye!")


class InfiniteScreen(UIScreen):
    title = u"You need to use 'q' to quit"

    def __init__(self, app):
        super().__init__(app)
        self.continue_count = 0

    def refresh(self, args=None):
        """Print text to user with number of continue clicked"""
        super().refresh(args)
        text = TextWidget("You clicked {} times on continue".format(self.continue_count))
        self._window += [CenterWidget(text), ""]
        return True

    def input(self, args, key):
        """Catch 'c' keys for continue and increase counter"""
        if key == Prompt.CONTINUE:
            self.continue_count += 1
            return INPUT_PROCESSED

        return key


if __name__ == "__main__":
    a = App("Hello World")
    s = InfiniteScreen(a)
    a.schedule_screen(s)
    a.run()
