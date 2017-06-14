#!/bin/python3

from simpleline import INPUT_PROCESSED
from simpleline.adv_widgets import PasswordDialog
from simpleline.base import UIScreen, App
from simpleline.render.prompt import Prompt
from simpleline.render.widgets import TextWidget, ColumnWidget, CenterWidget


class Hub(UIScreen):
    title = u"Hub"

    KEY_USER = "1"
    KEY_SURNAME = "2"
    KEY_PASSWORD = "3"

    def __init__(self, app):
        super().__init__(app)
        self._name_spoke = SetName(app, "First name", "John")
        self._surname_spoke = SetName(app, "Surname", "Doe")
        self._pass_spoke = PasswordDialog(app)

    def refresh(self, args=None):
        super().refresh(args)

        header = TextWidget("Please complete all the spokes to continue")
        header = CenterWidget(header)

        left = [TextWidget("{}) First name".format(self.KEY_USER)),
                TextWidget("   {}".format(self._name_spoke.value)),
                TextWidget("{}) Surname".format(self.KEY_SURNAME)),
                TextWidget("   {}".format(self._surname_spoke.value))]
        right = [TextWidget("{}) Password".format(self.KEY_PASSWORD))]

        if self._pass_spoke.answer:
            right.append(TextWidget("   Pasword is set"))

        col = ColumnWidget([(30, left), (30, right)], 5)
        self._window += [header, "", "", col, ""]
        return True

    def input(self, args, key):
        """Run spokes based on the user choice"""
        if key == self.KEY_USER: # set first name
            self.app.switch_screen_with_return(self._name_spoke)
            return INPUT_PROCESSED
        elif key == self.KEY_SURNAME: # set surname
            self.app.switch_screen_with_return(self._surname_spoke)
            return INPUT_PROCESSED
        elif key == self.KEY_PASSWORD: # set password
            self.app.switch_screen_with_return(self._pass_spoke)
            return INPUT_PROCESSED
        elif key == Prompt.CONTINUE:
            if self._name_spoke and self._surname_spoke and self._pass_spoke.answer:
                return key
            else: # catch 'c' key if not everything set
                return INPUT_PROCESSED
        else:
            return key

    def prompt(self, args=None):
        """Add information to prompt for user"""
        prompt = super().prompt(args)
        prompt.add_option("1,2,3", "to enter spokes")
        return prompt


class SetName(UIScreen):
    title = u"SetName"

    def __init__(self, app, message, def_value):
        super().__init__(app)
        self._value = def_value or ""
        self._message = message

    def refresh(self, args=None):
        """Write message to user"""
        super().refresh(args)
        w = TextWidget(self._message)
        self._window += [CenterWidget(w), ""]
        return True

    def prompt(self, args=None):
        """Take user input"""
        self._value = self.app.raw_input("Write your name: ")
        self.close()

    @property
    def value(self):
        return self._value


if __name__ == "__main__":
    a = App("Hubs and Spokes")
    s = Hub(a)
    a.schedule_screen(s)
    a.run()
