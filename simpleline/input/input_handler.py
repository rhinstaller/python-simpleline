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

from simpleline import App
from simpleline.event_loop.signals import InputReadySignal
from simpleline.render.widgets import TextWidget


class InputHandler(object):

    def __init__(self, pass_function=None, callback=None):
        super().__init__()
        self._input_lock = threading.Lock()

        self._input = None
        self._input_callback = callback
        self._input_error_counter = 0
        self._input_thread = None
        self._input_received = False
        self._width = App.get_scheduler().io_manager.width

        if pass_function:
            self._getpass_func = pass_function
        else:
            self._getpass_func = getpass.getpass

        App.get_event_loop().register_signal_handler(InputReadySignal,
                                                     self._input_received_handler)

    def _input_received_handler(self, signal, args):
        if signal.source is not self:
            return

        self._input_received = True
        self._user_input = signal.data
        # wait for the input thread to finish
        self._input_thread.join()

        # call async callback
        if self._input_callback is not None:
            cb = self._input_callback
            self._input_callback = None

            cb(self._user_input)

    @property
    def value(self):
        """Return user input.

        :returns: String or None if no is input received.
        """
        return self._input

    def set_pass_func(self, getpass_func):
        """Set a function for getting passwords."""
        self._getpass_func = getpass_func

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

    def get_input(self, prompt, hidden=False):
        """Use prompt to ask for user input and wait (non-blocking) on user input.

        This is an asynchronous call. If you want to wait for user input then use
        the `wait_on_input` method. If you want to get results asynchronously then register
        callback in constructor or by the `set_callback` method.

        Check if user input was already received can be done by the `input_received` method call.

        :param prompt: Ask user what you want to get.
        :type prompt: String or Prompt instance.

        :param hidden: Hide echo of the keys from user.
        :type hidden: bool

        :returns: User input.
        :rtype: str
        """
        self._check_input_thread_running()
        self._start_user_input_async(prompt, hidden)

    def get_input_without_check(self, prompt, hidden=False):
        """Reads user input without checking if someone is already waiting for input.

        This works the same as `get_user_input` but ignore checks if there is somebody waiting on input.
        When the user input is taken, all the waiting threads will get the same input.

        WARNING:
            This may be necessary in some situations, however, it can cause errors which are hard to find!


        See `get_user_input()` method.
        """
        self._start_user_input_async(prompt, hidden)

    def wait_on_input(self):
        App.get_event_loop().process_signals(InputReadySignal)
        return self._input  # return the user input

    def _check_input_thread_running(self):
        if self._input_thread is not None and self._input_thread.is_alive():
            raise KeyError("Can't run multiple input threads at the same time!")

    def _start_user_input_async(self, prompt, hidden):
        self._input_received = False
        self._input_thread = threading.Thread(target=self._thread_input, name="InputThread",
                                              args=(prompt, hidden))
        self._input_thread.daemon = True
        self._input_thread.start()

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

        App.get_event_loop().enqueue_signal(InputReadySignal(self, data))

    def _prompt_to_text(self, prompt):
        widget = TextWidget(str(prompt))
        widget.render(self._width)
        lines = widget.get_lines()
        return "\n".join(lines) + " "

    def _get_input(self):
        return input()
