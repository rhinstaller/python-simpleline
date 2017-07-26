#!/bin/python3

from simpleline.base import App
from simpleline.render.adv_widgets import PasswordDialog
from simpleline.render.prompt import Prompt
from simpleline.render.screen import UIScreen
from simpleline.render import InputState
from simpleline.render.widgets import TextWidget, ColumnWidget, CenterWidget


class Hub(UIScreen):

    KEY_USER = "1"
    KEY_SURNAME = "2"
    KEY_PASSWORD = "3"

    def __init__(self):
        super().__init__("Hub")
        self._name_spoke = SetNameScreen("First name", "John")
        self._surname_spoke = SetNameScreen("Surname", "Doe")
        self._pass_spoke = PasswordDialog()

    def refresh(self, args=None):
        super().refresh(args)

        header = TextWidget("Please complete all the spokes to continue")
        header = CenterWidget(header)
        self.window.add(header)

        left = [TextWidget("{}) First name".format(self.KEY_USER)),
                TextWidget("   {}".format(self._name_spoke.value)),
                TextWidget("{}) Surname".format(self.KEY_SURNAME)),
                TextWidget("   {}".format(self._surname_spoke.value))]
        right = [TextWidget("{}) Password".format(self.KEY_PASSWORD))]

        if self._pass_spoke.answer:
            right.append(TextWidget("   Password is set"))

        col = ColumnWidget([(30, left), (30, right)], 5)
        self.window.add_separator(2)
        self.window.add(col)
        self.window.add_separator()

    def input(self, args, key):
        """Run spokes based on the user choice."""
        if key == self.KEY_USER:  # set first name
            App.get_scheduler().push_screen(self._name_spoke)
            return InputState.PROCESSED
        elif key == self.KEY_SURNAME:  # set surname
            App.get_scheduler().push_screen(self._surname_spoke)
            return InputState.PROCESSED
        elif key == self.KEY_PASSWORD:  # set password
            App.get_scheduler().push_screen(self._pass_spoke)
            return InputState.PROCESSED
        elif key == Prompt.CONTINUE:
            if self._name_spoke and self._surname_spoke and self._pass_spoke.answer:
                return key
            else:  # catch 'c' key if not everything set
                return InputState.DISCARDED
        else:
            return key

    def prompt(self, args=None):
        """Add information to prompt for user."""
        prompt = super().prompt(args)
        prompt.add_option("1,2,3", "to enter spokes")
        return prompt


class SetNameScreen(UIScreen):

    def __init__(self, message, def_value):
        super().__init__()
        self._value = def_value or ""
        self._message = message

    def refresh(self, args=None):
        """Write message to user."""
        super().refresh(args)
        w = TextWidget(self._message)
        self.window.add(CenterWidget(w))

    def prompt(self, args=None):
        """Take user input."""
        self._value = self.get_user_input("Write your name: ")
        self.close()

    @property
    def value(self):
        return self._value


if __name__ == "__main__":
    App.initialize()
    screen = Hub()
    App.get_scheduler().schedule_screen(screen)
    App.run()
