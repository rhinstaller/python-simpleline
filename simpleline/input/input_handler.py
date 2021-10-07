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

import sys

from simpleline import App
from simpleline.event_loop.signals import InputReadySignal
from simpleline.render.widgets import TextWidget
from simpleline.input.input_threading import InputThreadManager, InputRequest

__all__ = ["InputHandler", "PasswordInputHandler"]


class InputHandler(object):

    def __init__(self, callback=None, source=None):
        """Class to handle input from the terminal.

        This class is designed to be instantiated on place where it should be used.
        The main method is `get_input()` which is non-blocking asynchronous call. It can be used
        as synchronous call be calling the `wait_on_input` method.

        To get result from this class use the `value` property.

        :param callback: You can specify callback which will be called when user give input.
        :type callback: Callback function with one argument which will be user input.

        :param source: Source of this input. It will be helpful in case of debugging an issue.
        :type source: Class which will process an input from this InputHandler.
        """
        super().__init__()
        self._input = None
        self._input_callback = callback
        self._input_received = False
        self._input_successful = False
        self._skip_concurrency_check = False
        self._source = source

        self._register_input_ready_signal()

    def _register_input_ready_signal(self):
        App.get_event_loop().register_signal_handler(InputReadySignal,
                                                     self._input_received_handler)

    def _input_received_handler(self, signal, args):
        if signal.input_handler_source != self:
            return

        self._input_received = True
        self._input_successful = signal.success

        if not self._input_successful:
            return

        self._input = signal.data

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
    def source(self):
        """Get source of this input.

        :returns: Anything probably UIScreen.
        """
        return self._source

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

        Please check the `input_successful` method to test the input.
        """
        # we already received input from user
        if self._input_received:
            return

        while not self._input_received:
            App.get_event_loop().process_signals(InputReadySignal)

    def input_successful(self):
        """Was input successful?

        :returns: bool
        """
        return self._input_successful

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
        self._clear_input()
        self._invoke_input_thread(prompt)

    def _invoke_input_thread(self, prompt):
        thread_object = self.create_thread_object(prompt)
        InputThreadManager.get_instance().start_input_thread(thread_object,
                                                             not self._skip_concurrency_check)

    def create_thread_object(self, prompt):
        """Create thread object containing all the information how to get user input.

        :returns: Instance of class inherited from `simpleline.input.InputThread`.
        """
        return InputHandlerRequest(App.get_configuration().width, prompt, self)

    def _clear_input(self):
        self._input_received = False
        self._input = None


class InputHandlerRequest(InputRequest):
    """This is thread object to get input from user without blocking main thread."""

    def __init__(self, width, prompt, input_handler):
        """Create request object to get input in InputThreadManager.

        :param width: Width of the screen prompt.
        :type width: int

        :param prompt: Input prompt.
        :type prompt: Instance of `simpleline.render.prompt.Prompt` class.

        :param input_handler: InputHandler instance which created this object.
        :type input_handler: InputHandler based instance.
        """
        super().__init__(input_handler, input_handler.source)
        self._width = width
        self._prompt = prompt

    def get_input(self):
        """This method is responsible for interruptable user input.

        It is expected to be used in a thread started on demand
        and returns the input via the communication Queue.
        """
        # lock acquired, we can run input
        try:
            data = self._ask_input()
        except EOFError:
            data = ""

        return data

    def text_prompt(self):
        widget = TextWidget(str(self._prompt))
        widget.render(self._width)
        lines = widget.get_lines()
        return "\n".join(lines) + " "

    def _ask_input(self):
        text_prompt = self.text_prompt()
        sys.stdout.write(text_prompt)
        sys.stdout.flush()

        return self._get_input()

    def _get_input(self):
        return input()


class PasswordInputHandler(InputHandler):

    def __init__(self, callback=None, source=None):
        """Class to handle hidden password input from the terminal.

        This class is designed to be instantiated on place where it should be used.
        The main method is `get_input()` which is non-blocking asynchronous call. It can be used
        as synchronous call be calling the `wait_on_input` method.

        To get result from this class use the `value` property.

        :param callback: You can specify callback which will be called when user give input.
        :type callback: Callback function with one argument which will be user input.

        :param source: Source of this input. It will be helpful in case of debugging an issue.
        :type source: Class which will process an input from this InputHandler.
        """
        super().__init__(callback=callback, source=source)
        self._getpass_func = App.get_configuration().password_function

    def set_pass_func(self, getpass_func):
        """Set a function for getting passwords."""
        if not getpass_func:
            return

        self._getpass_func = getpass_func

    def create_thread_object(self, prompt):
        """Return PasswordInputThread for getting user password."""
        return PasswordInputHandlerRequest(App.get_configuration().width, prompt, self,
                                           self._getpass_func)


class PasswordInputHandlerRequest(InputHandlerRequest):
    """Similar as InputHandlerRequest but don't echo user keys."""

    def __init__(self, width, prompt, input_handler, getpass_func):
        """Create request object to get password input in InputThreadManager.

        :param width: Width of the screen prompt.
        :type width: int

        :param prompt: Input prompt.
        :type prompt: Instance of `simpleline.render.prompt.Prompt` class.

        :param input_handler: InputHandler instance which created this object.
        :type input_handler: InputHandler based instance.

        :param getpass_func: Function to get user password.
        :type getpass_func: Function which gets prompt as only parameter and returns user input
                            string.
        """
        super().__init__(width, prompt, input_handler)
        self._getpass_func = getpass_func

    def _ask_input(self):
        text_prompt = self.text_prompt()

        return self._getpass_func(text_prompt)
