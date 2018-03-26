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

from simpleline import App
from simpleline.event_loop import ExitMainLoop
from simpleline.event_loop.signals import ExceptionSignal
from simpleline.render.prompt import Prompt
from simpleline.input.input_handler import InputHandler, PasswordInputHandler

from simpleline.logging import get_simpleline_logger

log = get_simpleline_logger()


class InputManager(object):

    def __init__(self, ui_screen):
        """Processor for user input.

        This class is mainly helper class for ScreenScheduler.

        :param ui_screen: Screen associated with this input manager.
        :type ui_screen: The `simpleline.render.screen.UIScreen` based instance.
        """
        super().__init__()
        self._ui_screen = ui_screen
        self._input_error_counter = 0
        self._input_error_threshold = 5
        self._input_args = None

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

    def get_input(self, args=None):
        """Get input from user.

        :param args: Arguments passed in when UIScreen was scheduled.
        :type args: Anything.
        """
        prompt = self._ui_screen.prompt(args)
        if not self._is_input_expected(prompt):
            return

        self._input_args = args

        if not self._ui_screen.hide_user_input:
            handler = InputHandler()
        else:
            handler = PasswordInputHandler()
            if self._ui_screen.password_func:
                handler.set_pass_func(self._ui_screen.password_func)

        handler.set_callback(self.process_input)
        handler.get_input(prompt)

    def _is_input_expected(self, prompt):
        """Check if user handled input processing some other way.

        Do nothing if user did handled user input.

        :returns: True if prompt is set and we can use it to get user input.
                  False if prompt is not available, which means that user handled input on their
                  own.
        """
        # None means prompt handled the input by itself -> continue
        if prompt is None:
            self._input_error_counter = 0
            return False
        else:
            return True

    def process_input(self, user_input):
        """Process input from the screens.

        :param user_input: User input string.
        :type user_input: String.

        :raises: ExitMainLoop or any other kind of exception from screen processing.
        """
        # process the input, if it wasn't processed (valid)
        # increment the error counter
        try:
            result = self._process_input(user_input)
        except ExitMainLoop:
            raise
        except Exception:    # pylint: disable=broad-except
            App.get_event_loop().enqueue_signal(ExceptionSignal(self))
            return

        if result.was_successful():
            self._input_error_counter = 0
        else:
            self._input_error_counter += 1

        App.get_scheduler().process_input_result(result, self.input_error_threshold_exceeded)

    def _process_input(self, key):
        """Method called internally to process unhandled input key presses.

        :param key: The string entered by user.
        :type key: String.

        :return: Return state result object.
        :rtype: `simpleline.render.in_out_manager.UserInputResult` class.

        :raises: Anything the Screen can raise in the input processing.
        """
        from simpleline.render.screen import InputState
        # delegate the handling to active screen first
        try:
            key = self._ui_screen.input(self._input_args, key)
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
