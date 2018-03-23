# Class for managing input and output for application.
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

from simpleline.render.screen import InputState
from simpleline.event_loop import ExitMainLoop
from simpleline.render.prompt import Prompt
from simpleline.input.input_handler import InputHandler, PasswordInputHandler

from simpleline.logging import get_simpleline_logger

log = get_simpleline_logger()


class InputManager(object):

    def __init__(self):
        """Processor for user input.

        This class is mainly helper class for ScreenScheduler.
        """
        super().__init__()
        self._input_error_counter = 0
        self._input_error_threshold = 5

    @property
    def input_error_counter(self):
        """Return how many times the user provided bad input."""
        return self._input_error_counter

    @property
    def input_error_threshold_exceeded(self):
        """Did the error counter pass the threshold?

        The screen should be redraw.
        """
        errors = self._input_error_counter % self._input_error_threshold
        return errors == 0

    def get_input(self, prompt, callback, hidden, pass_func=None):
        """Get input from user.

        :param prompt: Object to explain what is required from a user.
        :type prompt: String or `simpleline.render.prompt.Prompt` instance.

        :param callback: Callback which will be called when input received.
        :type callback: Function with one parameter (user input).

        :param hidden: Is user input a password?
        :type hidden: bool

        :param pass_func: Function to get password which takes one argument.
        :type pass_func: Function with one argument which is text form of prompt.
        """
        if not self._is_input_expected(prompt):
            return

        if not hidden:
            handler = InputHandler()
        else:
            handler = PasswordInputHandler()
            if pass_func:
                handler.set_pass_func(pass_func)

        handler.set_callback(callback)
        handler.get_input(prompt)

    def _is_input_expected(self, prompt):
        """Check if user handled input processing some other way.

        Do nothing if user did handled user input.

        :returns: True if prompt is set and we can use it to get user input.
                  False if prompt is not available, which means that user handled input on their own.
        """
        # None means prompt handled the input by itself -> continue
        if prompt is None:
            self._input_error_counter = 0
            return False
        else:
            return True

    def process_input(self, active_screen, user_input):
        """Process input from the screens.

        Result of the processing is saved in the `processed_result` property.

        :param active_screen: Screen demanding this input processing.
        :type active_screen: Classed based on `simpleline.render.screen.UIScreen`.

        :param user_input: User input string.
        :type user_input: String.

        :raises: ExitMainLoop or any other kind of exception from screen processing.

        :return: Return data object with result status and state.
        :rtype: `simpleline.render.in_out_manager.UserInputResult` class.
        """
        # process the input, if it wasn't processed (valid)
        # increment the error counter
        result = self._process_input(active_screen, user_input)
        if result.was_successful():
            self._input_error_counter = 0
        else:
            self._input_error_counter += 1
        return result

    def _process_input(self, active_screen, key):
        """Method called internally to process unhandled input key presses.

        :param active_screen: Screen for input processing.
        :type active_screen: Class based on `simpleline.render.screen_stack.screen_data`.

        :param key: The string entered by user.
        :type key: String.

        :return: Return state result object.
        :rtype: `simpleline.render.in_out_manager.UserInputResult` class.

        :raises: Anything the Screen can raise in the input processing.
        """
        # delegate the handling to active screen first
        try:
            key = active_screen.ui_screen.input(active_screen.args, key)
            if key == InputState.PROCESSED:
                return UserInputAction.NOOP
            elif key == InputState.PROCESSED_AND_REDRAW:
                return UserInputAction.REDRAW
            elif key == InputState.PROCESSED_AND_CLOSE:
                return UserInputAction.CLOSE
            elif key == InputState.DISCARDED:
                return UserInputAction.INPUT_ERROR
        except ExitMainLoop:
            raise

        # global refresh command
        if key == Prompt.REFRESH:
            return UserInputAction.REDRAW

        # global close command
        if key == Prompt.CONTINUE:
            return UserInputAction.CLOSE

        # global quit command
        if key == Prompt.QUIT:
            return UserInputAction.QUIT

        if key is None:
            log.warning("Returned key from screen is None. "
                        "This could be missing return in a screen input method?")

        return UserInputAction.INPUT_ERROR


class UserInputAction(Enum):
    """Store user input result."""
    INPUT_ERROR = -1
    NOOP = 0
    REDRAW = 5
    CLOSE = 6
    QUIT = 7

    def was_successful(self):
        return self != UserInputAction.INPUT_ERROR
