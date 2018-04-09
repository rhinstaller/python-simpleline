# Base class for text window screens.
#
# Copyright (C) 2017  Red Hat, Inc.
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
# Author(s): Jiri Konecny <jkonecny@redhat.com>
#

from enum import Enum

from simpleline import App
from simpleline.render.containers import WindowContainer
from simpleline.render.prompt import Prompt
from simpleline.render.screen.signal_handler import SignalHandler
from simpleline.render.screen.input_manager import InputManager
from simpleline.utils.i18n import _

__all__ = ["UIScreen", "InputState"]


class UIScreen(SignalHandler):
    """Base class representing one TUI Screen.

    Shares some API with anaconda's GUI to make it easy for devs to create similar UI
    with the familiar API.
    """

    def __init__(self, title=None, screen_height=30):
        """ Constructor of the TUI screen.

        :param title: Title line of the screen.
        :type title: str

        :param screen_height: height of the screen (useful for printing long widgets)
        :type screen_height: int (the value must be bigger than 4)
        """
        self._title = title
        self._screen_height = screen_height
        self._screen_ready = False

        # ask for password
        self._hide_user_input = False
        self._password_func = None

        # do not print separator for this screen
        self._no_separator = False

        # list that holds the content to be printed out
        self._window = WindowContainer(self.title)

        # should the input be required after draw
        self._input_required = True

        # index of the page (subset of screen) shown during show_all
        # indexing starts with 0
        self._page = 0

        self._input_manager = InputManager(ui_screen=self)

    def __str__(self):
        """For easier logging."""
        return self.__class__.__name__

    @property
    def title(self):
        """Screen title."""
        return self._title

    @title.setter
    def title(self, title):
        """Set screen title.

        Set `None` to remove title.
        """
        self._title = title

    @property
    def password_func(self):
        """Get password function.

        This is function with one argument to get password from command line.
        """
        return self._password_func

    @password_func.setter
    def password_func(self, value):
        """Set password function.

        :param value: Function to get password from a command line.
        :type value: Function with one argument which is text representation of prompt.
        """
        self._password_func = value

    @property
    def screen_ready(self):
        """This screen is ready for use."""
        return self._screen_ready

    @screen_ready.setter
    def screen_ready(self, screen_ready):
        """Set ready status for this screen."""
        self._screen_ready = screen_ready

    @property
    def input_required(self):
        """Return if the screen requires input."""
        return self._input_required

    @input_required.setter
    def input_required(self, input_required):
        """Set if the screen should require input."""
        self._input_required = input_required

    @property
    def no_separator(self):
        """Should we print separator for this screen?

        :returns: True to print separator before this screen (default).
                  False do not print separator.
        """
        return self._no_separator

    @no_separator.setter
    def no_separator(self, no_separator):
        """Print or do not print separator.

        :param no_separator: Specify if the separator should be printed.
        :type no_separator: bool (default: False).
        """
        self._no_separator = no_separator

    @property
    def hide_user_input(self):
        """Hide typed user input.

        This is main solution how to ask for password.

        :returns: True if user input should be hidden.
                  False otherwise (default).
        """
        return self._hide_user_input

    @hide_user_input.setter
    def hide_user_input(self, hide_input):
        """Should be the user input hidden.

        :param hide_input: True if user input should be hidden.
                          False if not (default).
        :type hide_input: bool (default: False).
        """
        self._hide_user_input = hide_input

    @property
    def window(self):
        """Return WindowContainer instance."""
        return self._window

    @window.setter
    def window(self, window):
        """Set base WindowContainer instance.

        :param window: Base window container containing other widgets and containers.
        :type window: Instance of `simpleline.render.containers.WindowContainer` class.
        """
        self._window = window

    def get_user_input(self, message, hidden=False):
        """Get immediately input from the user.

        Use this with cautious. Never call this in middle of rendering or when other
        input is already waiting. It is recommended to use `self.input_required` instead.

        :param message: Message prompt for the user.
        :type message: str

        :param hidden: Do not echo user input (password typing).
        :type hidden: bool
        """
        return self._input_manager.get_input_blocking(message, hidden)

    def setup(self, args):
        """Do additional setup right before this screen is used.

        It is mandatory to call this ancestor method in the child class to set ready status.

        :param args: arguments for the setup
        :type args: array of values
        :return: whether this screen should be scheduled or not
        :rtype: bool
        """
        self._screen_ready = True
        App.get_event_loop().register_signal_source(self)
        return True

    def refresh(self, args=None):
        """Method which prepares the content desired on the screen to `self.window`.

        :param args: optional argument passed from switch_screen calls
        :type args: anything
        """
        self.window = WindowContainer(self._title)

    def _print_widget(self, widget):
        """Prints a widget (could be longer than the screen height) with user interaction (when needed).

        :param widget: widget to print
        :type widget: Widget instance
        """
        # TODO: Work even for lower screen_height than 4
        pos = 0
        lines = widget.get_lines()
        num_lines = len(lines)

        if num_lines == 0:
            return

        prompt_height = 2
        real_screen_height = self._screen_height - prompt_height

        if num_lines < real_screen_height:
            # widget plus prompt are shorter than screen height, just print the widget
            print(u"\n".join(lines))
            return

        # long widget, print it in steps and prompt user to continue
        last_line = num_lines - 1
        while pos <= last_line:
            if pos + real_screen_height > last_line:
                # enough space to print the rest of the widget plus regular
                # prompt (2 lines)
                for line in lines[pos:]:
                    print(line)
                pos += self._screen_height - 1
            else:
                # print part with a prompt to continue
                for line in lines[pos:(pos + real_screen_height)]:
                    print(line)
                custom_prompt = Prompt(_("\nPress %s to continue") % Prompt.ENTER)
                self._ask_user_input_blocking(custom_prompt)
                pos += real_screen_height

    def _ask_user_input_blocking(self, prompt):
        return self._input_manager.get_input_blocking(prompt, False)

    def show_all(self):
        """Print WindowContainer in `self.window` with all its content."""
        self.window.render(App.get_width())
        self._print_widget(self.window)

    def input(self, args, key):
        """Method called to process input. If the input is not handled here, return it.

        :param key: input string to process
        :type key: str
        :param args: optional argument passed from switch_screen calls
        :type args: anything
        :return: return `simpleline.render.InputState.PROCESSED` if key was handled,
                 `simpleline.render.InputState.DISCARDED` if the screen should not process input
                 on the scheduler and key if you want it to.
        :rtype: `simpleline.render.InputState` enum | str
        """
        return key

    def get_input_with_error_check(self, args):
        """Get user input and redraw if user add too many invalid inputs.

        This method should be used only by ScreenScheduler.

        :param args: Arguments passed in when scheduling this screen.
        :type args: Anything.
        """
        self._input_manager.get_input(args=args)

    def prompt(self, args=None):
        """Return the text to be shown as prompt or handle the prompt and return None.

        :param args: optional argument passed from switch_screen calls
        :type args: anything
        :return: returns an instance of Prompt with text to be shown next to the prompt
                 for input or None to skip further input processing
        :rtype: Prompt instance|None
        """
        prompt = Prompt()
        prompt.add_refresh_option()
        prompt.add_continue_option()
        prompt.add_quit_option()
        return prompt

    def closed(self):
        """Callback when this screen is closed."""
        pass


class InputState(Enum):
    PROCESSED = 1
    PROCESSED_AND_REDRAW = 2
    PROCESSED_AND_CLOSE = 3
    DISCARDED = 0
