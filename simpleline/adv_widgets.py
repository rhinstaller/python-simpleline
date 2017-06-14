# base TUIObject for Anaconda TUI
#
# Copyright (C) 2012  Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# the GNU General Public License v.2, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY expressed or implied, including the implied warranties of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.  You should have received a copy of the
# GNU General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.  Any Red Hat trademarks that are incorporated in the
# source code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission of
# Red Hat, Inc.
#
import sys

from simpleline import INPUT_PROCESSED
from simpleline import widgets
from simpleline.base import UIScreen
from simpleline.render.prompt import Prompt
from simpleline.utils.i18n import _, N_, C_


class ErrorDialog(UIScreen):
    """Dialog screen for reporting errors to user."""

    title = N_("Error")

    def __init__(self, app, message):
        """
        :param app: the running application reference
        :type app: instance of App class

        :param message: the message to show to the user
        :type message: str
        """
        super().__init__(app)
        self._message = message

    def refresh(self, args=None):
        super().refresh(args)
        text = widgets.TextWidget(self._message)
        self._window += [widgets.CenterWidget(text), ""]
        return True

    def prompt(self, args=None):
        return Prompt(_("Press %s to exit") % Prompt.ENTER)

    def input(self, args, key):
        """This dialog is closed by any input.

        And causes the program to quit.
        """
        sys.exit(1)


class PasswordDialog(UIScreen):
    """Dialog screen for password input."""

    title = N_("Password")

    def __init__(self, app, message=None):
        """
        :param app: the running application reference
        :type app: instance of App class

        :param message: password prompt question
        :type message: string
        """
        super().__init__(app)
        self._message = message or _("Enter your passphrase")
        self._password = None

    def refresh(self, args=None):
        super().refresh(args)
        text = widgets.TextWidget(self._message)
        self._window += [widgets.CenterWidget(text), ""]
        return True

    def prompt(self, args=None):
        self._password = self.app.raw_input(_("Passphrase: "), hidden=True)
        if not self._password:
            return None
        else:
            # this may seem innocuous, but it's really a giant hack; we should
            # not be calling close() from prompt(), but the input handling code
            # in the TUI is such that without this very simple workaround, we
            # would be forever pelting users with a prompt to enter their pw
            self.close()

    @property
    def answer(self):
        """The response can be None (no response) or the password entered."""
        return self._password

    def input(self, args, key):
        if key:
            self._password = key
            self.close()
            return True
        else:
            return False


class YesNoDialog(UIScreen):
    """Dialog screen for Yes - No questions."""

    title = N_("Question")

    def __init__(self, app, message):
        """
        :param app: the running application reference
        :type app: instance of App class

        :param message: the message to show to the user
        :type message: unicode
        """
        super().__init__(app)
        self._message = message
        self._response = None

    def refresh(self, args=None):
        super().refresh(args)
        text = widgets.TextWidget(self._message)
        self._window += [widgets.CenterWidget(text), ""]
        return True

    def prompt(self, args=None):
        return Prompt(_("Please respond '%(yes)s' or '%(no)s'") % {
            # TRANSLATORS: 'yes' as positive reply
            "yes": C_('TUI|Spoke Navigation', 'yes'),
            # TRANSLATORS: 'no' as negative reply
            "no": C_('TUI|Spoke Navigation', 'no')
        })

    def input(self, args, key):
        # TRANSLATORS: 'yes' as positive reply
        if key == C_('TUI|Spoke Navigation', 'yes'):
            self._response = True
            self.close()
            return None

        # TRANSLATORS: 'no' as negative reply
        elif key == C_('TUI|Spoke Navigation', 'no'):
            self._response = False
            self.close()
            return None

        else:
            return False

    @property
    def answer(self):
        """The response can be True (yes), False (no) or None (no response)."""
        return self._response


class HelpScreen(UIScreen):
    """Screen to display a help message."""

    title = N_("Help")

    def __init__(self, app, help_path):
        """
        :param app: the running application reference
        :type app: instance of App class

        :param help_path: help file name
        :type help_path: str
        """
        super().__init__(app)
        self.help_path = help_path

    def refresh(self, args=None):
        """ Show the help. """
        super().refresh(args)
        help_message = _("The help is not available.")

        if self.help_path:
            with open(self.help_path, 'r') as f:
                help_message = f.read()

        self._window += [widgets.TextWidget(help_message), ""]
        return True

    def input(self, args, key):
        """ Handle user input. """
        self.close()
        return INPUT_PROCESSED

    def prompt(self, args=None):
        return Prompt(_("Press %s to return") % Prompt.ENTER)
