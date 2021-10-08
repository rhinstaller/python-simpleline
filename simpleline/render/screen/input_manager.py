# Class for managing input and output for application.
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
# Author(s): Jiri Konecny <jkonecny@redhat.com>
#

from enum import Enum

from simpleline import App
from simpleline.event_loop import ExitMainLoop
from simpleline.event_loop.signals import ExceptionSignal
from simpleline.render.prompt import Prompt
from simpleline.input import InputHandler, PasswordInputHandler

from simpleline.logging import get_simpleline_logger

log = get_simpleline_logger()


class InputManager():

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
        self._skip_concurrency_check = False
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

    @property
    def skip_concurrency_check(self):
        """Should the concurrency check be skipped?

        :returns bool: True if the check should be skipped.
        """
        return self._skip_concurrency_check

    @skip_concurrency_check.setter
    def skip_concurrency_check(self, value):
        """Set if the concurrency check should be skipped when asking for user input.

        WARNING: Use this option with caution. When the concurrency check is disabled you
                 can easily get to unexpected behavior which is hard to debug.

        :param bool value: True to skip the concurrency check.
        """
        self._skip_concurrency_check = value

    def get_input_blocking(self, message, hidden):
        """Get blocking input from the user.

        :param message: Message prompt for the user.
        :type message: str

        :param hidden: Do not echo user input (password typing).
        :type hidden: bool
        """
        if hidden:
            handler = PasswordInputHandler(source=self)
            if self._ui_screen.password_func:
                handler.set_pass_func(self._ui_screen.password_func)
        else:
            handler = InputHandler(source=self)

        handler.skip_concurrency_check = self._skip_concurrency_check
        handler.get_input(message)
        handler.wait_on_input()
        return handler.value

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
            handler = InputHandler(source=self._ui_screen)
        else:
            handler = PasswordInputHandler(source=self._ui_screen)
            if self._ui_screen.password_func:
                handler.set_pass_func(self._ui_screen.password_func)

        handler.skip_concurrency_check = self._skip_concurrency_check
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
        except ExitMainLoop:  # pylint: disable=try-except-raise
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
        from simpleline.render.screen import InputState # pylint: disable=import-outside-toplevel
        # delegate the handling to active screen first
        key = self._ui_screen.input(self._input_args, key)
        if key == InputState.PROCESSED:
            return UserInputAction.NOOP

        if key == InputState.PROCESSED_AND_REDRAW:
            return UserInputAction.REDRAW

        if key == InputState.PROCESSED_AND_CLOSE:
            return UserInputAction.CLOSE

        if key == InputState.DISCARDED:
            return UserInputAction.INPUT_ERROR

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
