# Handle user input
#
# Copyright (C) 2018  Red Hat, Inc.
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

import threading
import sys
import getpass

from simpleline import App, DEFAULT_WIDTH
from simpleline.event_loop.signals import InputReadySignal
from simpleline.render.widgets import TextWidget


class InputHandler(object):

    def __init__(self, callback=None, width=DEFAULT_WIDTH):
        """Class to handle input from the terminal.

        This class is designed to be instantiated on place where it should be used.
        The main method is `get_input()` which is non-blocking asynchronous call. It can be used
        as synchronous call be calling the `wait_on_input` method.

        To get result from this class use the `value` property.

        :param callback: You can specify callback which will be called when user give input.
        :type callback: Callback function with one argument which will be user input.

        :param width: Width for user input.
        :type width: int
        """
        super().__init__()
        self._input_lock = threading.Lock()

        self._input = None
        self._input_callback = callback
        self._input_error_counter = 0
        self._input_thread = None
        self._input_received = False
        self._width = width
        self._skip_concurrency_check = False

        App.get_event_loop().register_signal_handler(InputReadySignal,
                                                     self._input_received_handler)

    def _input_received_handler(self, signal, args):
        if signal.source is not self:
            return

        self._input_received = True
        self._input = signal.data
        # wait for the input thread to finish
        self._input_thread.join()

        # call async callback
        if self._input_callback is not None:
            cb = self._input_callback
            self._input_callback = None

            cb(self._input)

    @property
    def value(self):
        """Return user input.

        :returns: String or None if no is input received.
        """
        return self._input

    @property
    def skip_concurrency_check(self):
        """Is this InputHandler skipping concurrency check?

        :returns bool
        """
        return self._skip_concurrency_check

    @skip_concurrency_check.setter
    def skip_concurrency_check(self, value):
        """Set if this InputHandler should skip concurrency check.

        Note if you skip this check, you can have unexpected behavior. Use with caution.

        :param value: True to skip the check, False if not.
        """
        self._skip_concurrency_check = value

    def set_callback(self, callback):
        """Set a callback to get user input asynchronously.

        :param callback: Callback called when user write their input.
        :type callback: Method with 1 argument which is user input: def cb(user_input)
        """
        self._input_callback = callback

    def input_received(self):
        """Was user input already received?

        :returns: True if yes, False otherwise.
        """
        return self._input_received

    def wait_on_input(self):
        """Blocks execution till the user input is received.

        Events will works as expected during this blocking.
        """
        # we already received input from user
        if self._input_received:
            return

        App.get_event_loop().process_signals(InputReadySignal)
        return

    def get_input(self, prompt):
        """Use prompt to ask for user input and wait (non-blocking) on user input.

        This is an asynchronous call. If you want to wait for user input then use
        the `wait_on_input` method. If you want to get results asynchronously then register
        callback in constructor or by the `set_callback` method.

        Check if user input was already received can be done by the `input_received` method call.

        :param prompt: Ask user what you want to get.
        :type prompt: String or Prompt instance.

        :returns: User input.
        :rtype: str
        """
        self._check_input_thread_running()
        self._start_user_input_async(prompt)

    def _check_input_thread_running(self):
        if self._skip_concurrency_check:
            return

        if self._input_thread is not None and self._input_thread.is_alive():
            raise KeyError("Can't run multiple input threads at the same time!")

    def _start_user_input_async(self, prompt):
        self._clear_input()

        self._input_thread = threading.Thread(target=self._thread_input, name="InputThread",
                                              args=[prompt])
        self._input_thread.daemon = True
        self._input_thread.start()

    def _clear_input(self):
        self._input_received = False
        self._input = None

    def _thread_input(self, prompt):
        """This method is responsible for interruptable user input.

        It is expected to be used in a thread started on demand
        and returns the input via the communication Queue.

        :param prompt: prompt to be displayed
        :type prompt: Prompt instance
        """
        if not self._input_lock.acquire(False):
            # raw_input is already running
            return
        else:
            # lock acquired, we can run input
            try:
                data = self._ask_input(prompt)
            except EOFError:
                data = ""
            finally:
                self._input_lock.release()

        App.get_event_loop().enqueue_signal(InputReadySignal(self, data))

    def _prompt_to_text(self, prompt):
        widget = TextWidget(str(prompt))
        widget.render(self._width)
        lines = widget.get_lines()
        return "\n".join(lines) + " "

    def _ask_input(self, prompt):
        text_prompt = self._prompt_to_text(prompt)
        sys.stdout.write(text_prompt)
        sys.stdout.flush()

        return self._get_input()

    def _get_input(self):
        return input()


class PasswordInputHandler(InputHandler):

    def __init__(self, callback=None, width=DEFAULT_WIDTH):
        """Class to handle hidden password input from the terminal.

        This class is designed to be instantiated on place where it should be used.
        The main method is `get_input()` which is non-blocking asynchronous call. It can be used
        as synchronous call be calling the `wait_on_input` method.

        To get result from this class use the `value` property.

        :param callback: You can specify callback which will be called when user give input.
        :type callback: Callback function with one argument which will be user input.

        :param width: Width for user input.
        :type width: int
        """
        super().__init__(callback=callback, width=width)
        self._getpass_func = getpass.getpass

    def set_pass_func(self, getpass_func):
        """Set a function for getting passwords."""
        self._getpass_func = getpass_func

    def _ask_input(self, prompt):
        text_prompt = self._prompt_to_text(prompt)

        return self._getpass_func(text_prompt)
