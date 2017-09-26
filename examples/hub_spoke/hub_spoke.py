#!/bin/python3

from simpleline import App
from simpleline.render.adv_widgets import PasswordDialog
from simpleline.render.containers import ListRowContainer
from simpleline.render.prompt import Prompt
from simpleline.render.screen import UIScreen, InputState
from simpleline.render.screen_handler import ScreenHandler
from simpleline.render.widgets import TextWidget, CenterWidget


class Hub(UIScreen):

    def __init__(self):
        super().__init__("Hub")
        self._name_spoke = SetNameScreen("First name", "John")
        self._surname_spoke = SetNameScreen("Surname", "Doe")
        self._password_spoke = PasswordDialog()
        self._container = None

    def refresh(self, args=None):
        super().refresh(args)

        # Add special header before our items
        header = TextWidget("Please complete all the spokes to continue")
        header = CenterWidget(header)
        self.window.add_with_separator(header, blank_lines=2)

        # Create a container and add items to it
        # It will add numbering, process user input and positioning for us.
        self._container = ListRowContainer(2)

        widget = self._create_name_widget()
        self._container.add(widget, self._push_screen_callback, self._name_spoke)

        widget = self._create_surname_widget()
        self._container.add(widget, self._push_screen_callback, self._surname_spoke)

        widget = self._create_password_widget()
        self._container.add(widget, self._push_screen_callback, self._password_spoke)

        self.window.add_with_separator(self._container)

    def _create_name_widget(self):
        msg = "First name"
        if self._name_spoke.value:
            msg += "\n{}".format(self._name_spoke.value)

        return TextWidget(msg)

    def _create_surname_widget(self):
        msg = "Surname"
        if self._surname_spoke.value:
            msg += "\n{}".format(self._surname_spoke.value)

        return TextWidget(msg)

    def _create_password_widget(self):
        msg = "Password"
        if self._password_spoke.answer:
            msg += "\nPassword set."

        return TextWidget(msg)

    def input(self, args, key):
        """Run spokes based on the user choice."""
        if self._container.process_user_input(key):
            return InputState.PROCESSED
        elif key == Prompt.CONTINUE:
            if self._name_spoke and self._surname_spoke and self._password_spoke.answer:
                return key
            else:  # catch 'c' key if not everything set
                return InputState.DISCARDED
        else:
            return key

    def _push_screen_callback(self, target_screen):
        ScreenHandler.push_screen(target_screen)

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
    ScreenHandler.schedule_screen(screen)
    App.run()
