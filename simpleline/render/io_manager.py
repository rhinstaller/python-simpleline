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

import threading
import sys
import getpass

from enum import Enum

from simpleline.render.screen import InputState
from simpleline.event_loop import ExitMainLoop
from simpleline.event_loop.signals import ExceptionSignal, InputReadySignal
from simpleline.render.prompt import Prompt
from simpleline.render.widgets import TextWidget

from simpleline.logging import get_simpleline_logger

log = get_simpleline_logger()


class InOutManager(object):

    def __init__(self, event_loop):
        """Processor for common user input and output.

        :param event_loop: Event loop used for the scheduler.
        :type event_loop: Class based on `simpleline.event_loop.AbstractEventLoop`.
        """
        super().__init__()
        self._input_lock = threading.Lock()
        self._input_error_counter = 0
        self._input_error_threshold = 5
        self._input_thread = None
        self._event_loop = event_loop
        self._getpass_func = getpass.getpass
        self._width = 80
        self._spacer = ""
        self._calculate_spacer()
        self._user_input = ""
        self._user_input_callback = None

        # save user input
        self._event_loop.register_signal_handler(InputReadySignal, self._user_input_received_handler)

    def _calculate_spacer(self):
        self._spacer = "\n".join(2 * [self._width * "="])

    @property
    def input_error_counter(self):
        """Return how many times the user provided bad input."""
        return self._input_error_counter

    @property
    def width(self):
        """Return width of the widgets."""
        return self._width

    @width.setter
    def width(self, width):
        """Set width of the widgets."""
        self._width = width
        self._calculate_spacer()

    @property
    def input_error_threshold_exceeded(self):
        """Did the error counter pass the threshold?

        The screen should be redraw.
        """
        errors = self._input_error_counter % self._input_error_threshold
        return errors == 0

    def _user_input_received_handler(self, signal, args):
        self._user_input = signal.data
        # wait for the input thread to finish
        self._input_thread.join()

        # call async callback
        if self._user_input_callback is not None:
            cb = self._user_input_callback
            self._user_input_callback = None

            cb(self._user_input)

    def set_pass_func(self, getpass_func):
        """Set a function for getting passwords."""
        self._getpass_func = getpass_func

    def draw(self, active_screen):
        """Draws the current `active_screen`.

        :param active_screen: Screen which should be draw to the console.
        :type active_screen: Classed based on `simpleline.render.screen.UIScreen`.
        """
        # get the widget tree from the screen and show it in the screen
        try:
            if not active_screen.ui_screen.no_separator:
                # separate the content on the screen from the stuff we are about to display now
                print(self._spacer)

            # print UIScreen content
            active_screen.ui_screen.show_all()
        except ExitMainLoop:
            raise
        except Exception:    # pylint: disable=broad-except
            self._event_loop.enqueue_signal(ExceptionSignal(self))

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

    def get_user_input_async(self, prompt, callback, hidden=False):
        """Reads user input asynchronously.

        User input will be retrieved by `simpleline.event_loop.signals.InputReadySignal` and then passed to
        the `callback` argument.

        :param prompt: Ask user what you want to get.
        :type prompt: String or Prompt instance.

        :param callback: Callback which will get user input as the only parameter.
        :type callback: Function with one parameter key.

        :param hidden: Hide echo of the keys from user.
        :type hidden: bool
        """
        if self._is_input_expected(prompt):
            self._user_input_callback = callback

            self._check_input_thread_running()
            self._start_user_input_async(prompt, hidden)

    def get_user_input(self, prompt, hidden=False):
        """Reads user input.

        You can wait on user input only once. Beware signals are processed when you
        are waiting for an input.

        :param prompt: Ask user what you want to get.
        :type prompt: String or Prompt instance.

        :param hidden: Hide echo of the keys from user.
        :type hidden: bool

        :returns: User input.
        :rtype: str
        """
        if not self._is_input_expected(prompt):
            return ""

        self._check_input_thread_running()

        self._start_user_input_async(prompt, hidden)
        return self._wait_on_user_input()

    def get_user_input_without_check(self, prompt, hidden=False):
        """Reads user input without checking if someone is already waiting for input.

        This works the same as `get_user_input` but ignore checks if there is somebody waiting on input.
        When the user input is taken, all the waiting threads will get the same input.

        WARNING:
            This may be necessary in some situations, however, it can cause errors which are hard to find!

        See `get_user_input()` method.
        """
        if self._is_input_expected(prompt):
            self._start_user_input_async(prompt, hidden)
            return self._wait_on_user_input()

    def _check_input_thread_running(self):
        if self._input_thread is not None and self._input_thread.is_alive():
            raise KeyError("Can't run multiple input threads at the same time!")

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

    def _start_user_input_async(self, prompt, hidden):
        self._input_thread = threading.Thread(target=self._thread_input, name="InputThread",
                                              args=(prompt, hidden))
        self._input_thread.daemon = True
        self._input_thread.start()

    def _wait_on_user_input(self):
        self._event_loop.process_signals(InputReadySignal)
        return self._user_input  # return the user input

    def _thread_input(self, prompt, hidden):
        """This method is responsible for interruptable user input.

        It is expected to be used in a thread started on demand
        and returns the input via the communication Queue.

        :param prompt: prompt to be displayed
        :type prompt: Prompt instance

        :param hidden: whether typed characters should be echoed or not
        :type hidden: bool
        """
        text_prompt = self._prompt_to_text(prompt)

        if not hidden:
            sys.stdout.write(text_prompt)
            sys.stdout.flush()

        if not self._input_lock.acquire(False):
            # raw_input is already running
            return
        else:
            # lock acquired, we can run input
            try:
                if hidden:
                    data = self._getpass_func(text_prompt)
                else:
                    data = self._get_input()
            except EOFError:
                data = ""
            finally:
                self._input_lock.release()

        self._event_loop.enqueue_signal(InputReadySignal(self, data))

    def _prompt_to_text(self, prompt):
        widget = TextWidget(str(prompt))
        widget.render(self._width)
        lines = widget.get_lines()
        return "\n".join(lines) + " "

    def _get_input(self):
        return input()

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
                return UserInputResult.PROCESSED
            elif key == InputState.DISCARDED:
                return UserInputResult.ERROR
        except ExitMainLoop:
            raise

        # global refresh command
        if key == Prompt.REFRESH:
            return UserInputResult.REFRESH

        # global close command
        if key == Prompt.CONTINUE:
            return UserInputResult.CONTINUE

        # global quit command
        if key == Prompt.QUIT:
            return UserInputResult.QUIT

        if key is None:
            log.warning("Returned key from screen is None. This could be missing return in a screen input method?")

        return UserInputResult.ERROR


class UserInputResult(Enum):
    """Store user input result."""
    ERROR = -1
    PROCESSED = 0
    REFRESH = 5
    CONTINUE = 6
    QUIT = 7

    def was_successful(self):
        return self != UserInputResult.ERROR
