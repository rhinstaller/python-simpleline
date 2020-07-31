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

import threading
from abc import ABCMeta, abstractmethod

from simpleline import App
from simpleline.logging import get_simpleline_logger
from simpleline.event_loop.signals import InputReceivedSignal, InputReadySignal

log = get_simpleline_logger()


INPUT_THREAD_NAME = "SimplelineInputThread"


class InputThreadManager():
    """Manager object for input threads.

    This manager helps with concurrent user input (still you really shouldn't do that).
    """

    __instance = None

    def __init__(self):
        super().__init__()
        self._input_stack = []
        self._processing_input = False

    @classmethod
    def create_new_instance(cls):
        instance = InputThreadManager()
        cls.__instance = instance

        instance._post_init_configuration() # pylint: disable=protected-access

    def _post_init_configuration(self):
        # pylint: disable=protected-access
        App.get_event_loop().register_signal_handler(InputReceivedSignal,
                                                     self.__instance._input_received_handler)

    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            cls.create_new_instance()

        return cls.__instance

    def _input_received_handler(self, signal, args):
        thread_object = self._input_stack.pop()
        thread_object.emit_input_ready_signal(signal.data)

        if thread_object.thread:
            thread_object.thread.join()

        # wait until used object ends
        for t in self._input_stack:
            t.emit_failed_input_ready_signal()
            if t.thread:
                t.thread.join()

        # remove all other items waiting for input
        self._input_stack.clear()
        self._processing_input = False

    def start_input_thread(self, input_thread_object, concurrent_check=True):
        """Start input thread to get user input.

        :param input_thread_object: Input thread object based on InputThread class.
        :param concurrent_check: Should the concurrent thread check be fatal? (default True).
        """
        self._input_stack.append(input_thread_object)
        self._check_input_thread_running(concurrent_check)
        self._start_user_input_async()

    def _check_input_thread_running(self, raise_concurrent_check):
        if len(self._input_stack) != 1:
            if not raise_concurrent_check:
                log.warning("Asking for multiple inputs with concurrent check bypassed, "
                            "last who asked wins! Others are dropped.")
            else:
                msg = ""
                for t in self._input_stack:
                    requester_source = t.requester_source or "Unknown"
                    msg += "Input handler: {} Input requester: {}\n".format(t.source,
                                                                            requester_source)

                msg.rstrip()

                raise KeyError("Can't run multiple input threads at the same time!\n"
                               "Asking for input:\n"
                               "{}".format(msg))

    def _start_user_input_async(self):
        thread_object = self._input_stack[-1]

        if self._processing_input:
            self._print_new_prompt(thread_object)
            return

        thread_object.initialize_thread()
        self._processing_input = True
        thread_object.start_thread()

    @staticmethod
    def _print_new_prompt(thread_object):
        prompt = thread_object.text_prompt()

        # print new prompt
        print(prompt, end="")


class InputRequest(metaclass=ABCMeta):
    """Base input request class.

    This should be overloaded for every InputHandler class. Purpose of this class is to print
    prompt and get input from user.

    The `run_input` method is the entry point for this class. Output from this method must be
    a user input.
    The `text_prompt` method is used to get textual representation of a prompt. This will be used
    on concurrent input to replace existing prompt to get new input.

    WARNING:
        The `run_input` method will run in a separate thread!
    """

    def __init__(self, source, requester_source=None):
        super().__init__()
        self._source = source
        self._requester_source = requester_source
        self.thread = None

    @property
    def source(self):
        """Get direct source of this input request.

        :returns: InputHandler instance.
        """
        return self._source

    @property
    def requester_source(self):
        """Get requester -- source of this input.

        :returns: Anything probably UIScreen based instance.
        """
        return self._requester_source

    def emit_input_ready_signal(self, input_data):
        """Emit the InputReadySignal signal with collected input data.

        :param input_data: Input data received.
        :type input_data: str
        """
        handler_source = self.source
        signal_source = self._get_request_source()

        new_signal = InputReadySignal(source=signal_source, input_handler_source=handler_source,
                                      data=input_data, success=True)
        App.get_event_loop().enqueue_signal(new_signal)

    def emit_failed_input_ready_signal(self):
        """Emit the InputReadySignal with failed state."""
        handler_source = self.source
        signal_source = self._get_request_source()

        new_signal = InputReadySignal(source=signal_source, input_handler_source=handler_source,
                                      data="", success=False)
        App.get_event_loop().enqueue_signal(new_signal)

    def _get_request_source(self):
        """Get user input request source.

        That means object who is using InputHandler.
        If this object is not specified then return InputHandler as a source.
        """
        return self.requester_source or self.source

    def initialize_thread(self):
        """Initialize thread for this input request.

        Do not call this directly! Will be called by InputThreadManager.
        """
        self.thread = threading.Thread(name=INPUT_THREAD_NAME, target=self.run)
        self.thread.daemon = True

    def start_thread(self):
        """Start input thread.

        Do not call this directly! Will be called by InputThreadManager.
        """
        self.thread.start()

    def run(self):
        """Run the `run_input` method and propagate input outside.

        Do not call this method directly. It will be called by InputThreadManager.
        """
        data = self.get_input()

        App.get_event_loop().enqueue_signal(InputReceivedSignal(self, data))

    @abstractmethod
    def text_prompt(self):
        """Get text representation of the user prompt.

        This will be used to get high priority input.

        :returns: String representation of the prompt or None if no prompt is present.
        """
        return None

    @abstractmethod
    def get_input(self):
        """Print prompt and get an input from user.

        ..NOTE: Overload this method in your class.

        Return this input from a function.
        """
        return ""
