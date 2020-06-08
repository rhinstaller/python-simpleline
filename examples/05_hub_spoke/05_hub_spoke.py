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
# Hub and spoke implementation.
#

# Advanced example of Simpleline use.
# Hub is the main screen from where you can go to spokes and do work in the spokes
# then you will return to the hub back. You can continue when all the required items
# is set.
# The example of containers use will be showed here.
#

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

        # Container will be used for spokes positioning. Container is always created in
        # the refresh() method.
        self._container = None

        self._create_spokes()

    def _create_spokes(self):
        """Create spokes and use their value."""

        # Create name spoke
        self._name_spoke = SetNameScreen("First name", "John")
        # Create surname spoke
        self._surname_spoke = SetNameScreen("Surname", "Doe")
        # Create the PasswordDialog advanced widget for getting password from a user.
        self._password_spoke = PasswordDialog()

    def refresh(self, args=None):
        """Refresh method is called always before the screen will be printed.

        All items for printing should be updated or created here.
        """
        # Init window container. The windows container will be erased here.
        # The window container is the base container. Everything for rendering should be put
        # into this container, including other containers.
        super().refresh(args)

        # Add the screen header message before our items.
        header = TextWidget("Please complete all the spokes to continue")
        header = CenterWidget(header)
        self.window.add_with_separator(header, blank_lines=2)

        # Create the empty container.
        # It will add numbering, process user input and positioning for us.
        self._container = ListRowContainer(2)

        # Create widget to get user name.
        widget = self._create_name_widget()
        # Add widget, callback, arguments to the container.
        #
        # widget - Widget we want to render. It will be numbered automatically.
        #          Could be container if needed.
        # callback - This callback will be called by the ListRowContainer.process_user_input() method
        #            when a user press the number of this item. Callback will get args passed as 3rd argument.
        # args - Argument for callback.
        self._container.add(widget, self._push_screen_callback, self._name_spoke)

        # Create surname widget and add it to the container.
        widget = self._create_surname_widget()
        self._container.add(widget, self._push_screen_callback, self._surname_spoke)

        # Create password widget and add it to the container.
        widget = self._create_password_widget()
        self._container.add(widget, self._push_screen_callback, self._password_spoke)

        # Add the ListRowContainer container to the WindowContainer container.
        self.window.add_with_separator(self._container)

    def _create_name_widget(self):
        """Create name spoke widget.

        Add the actual value below the spoke name.
        """
        msg = "First name"
        if self._name_spoke.value:
            msg += "\n{}".format(self._name_spoke.value)

        return TextWidget(msg)

    def _create_surname_widget(self):
        """Create surname spoke widget.

        Add the actual value below the spoke name.
        """
        msg = "Surname"
        if self._surname_spoke.value:
            msg += "\n{}".format(self._surname_spoke.value)

        return TextWidget(msg)

    def _create_password_widget(self):
        """Create password spoke widget.

        Add the "Password set" text below the spoke name if set.
        """
        msg = "Password"
        if self._password_spoke.answer:
            msg += "\nPassword set."

        return TextWidget(msg)

    def input(self, args, key):
        """Run spokes based on the user choice."""
        # Find out if a user pressed number for an existing widget and call the callback attached
        # to it with arguments passed in the refresh() method.
        # Return False if the input is not related to the widget.
        if self._container.process_user_input(key):
            # Do not process other input if spoke is entered.
            return InputState.PROCESSED
        # Block continue ('c') if everything is not set.
        elif key == Prompt.CONTINUE:
            if self._name_spoke and self._surname_spoke and self._password_spoke.answer:
                return key
            else:  # catch 'c' key if not everything set
                return InputState.DISCARDED
        else:
            return key

    def _push_screen_callback(self, target_screen):
        """Push target screen as new screen.

        Target screen is passed in as an argument in the refresh() method.
        """
        ScreenHandler.push_screen(target_screen)

    def prompt(self, args=None):
        """Add information to prompt for user."""
        prompt = super().prompt(args)
        # Give user hint that he can press 1, 2 or 3 to enter spokes.
        prompt.add_option("1,2,3", "to enter spokes")
        return prompt


class SetNameScreen(UIScreen):

    def __init__(self, message, def_value):
        """Create spoke for setting name and surname.

        :param message: Text message as the body for user.
        :param def_value: Default value for this spoke.
        """
        super().__init__()
        self._value = def_value
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
        """Return value set by a user in this spoke."""
        return self._value


if __name__ == "__main__":
    App.initialize()
    screen = Hub()
    ScreenHandler.schedule_screen(screen)
    App.run()
