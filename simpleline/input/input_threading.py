#
# Classes to handle thread for getting input from a user.
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
from abc import ABCMeta, abstractmethod

from simpleline import App
from simpleline.logging import get_simpleline_logger
from simpleline.event_loop.signals import InputReceivedSignal, InputReadySignal

log = get_simpleline_logger()


INPUT_THREAD_NAME = "SimplelineInputThread"


class InputThreadManager(object):
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

        instance._post_init_configuration()

    def _post_init_configuration(self):
        App.get_event_loop().register_signal_handler(InputReceivedSignal,
                                                     self.__instance._input_received_handler)

    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            cls.create_new_instance()

        return cls.__instance

    def _input_received_handler(self, signal, args):
        thread_object = self._input_stack[-1]
        handler_source = thread_object.source
        signal_source = self._get_request_source(thread_object)
        App.get_event_loop().enqueue_signal(InputReadySignal(source=signal_source,
                                                             input_handler_source=handler_source,
                                                             data=signal.data)
                                            )

        # wait until used object ends
        for t in self._find_running_thread_objects():
            t.thread.join()

        # remove last item -- it was satisfied
        self._input_stack.pop()

        self._processing_input = False
        self._start_user_input_async()

    def _get_request_source(self, thread_object):
        """Get user input request source.

        That means object who is using InputHandler.
        If this object is not specified then return InputHandler as a source.
        """
        return thread_object.requester_source or thread_object.source

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
                log.warning("Running concurrently multiple inputs. Last who asked wins! "
                            "Others will get input after this one.")
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
        if not self._input_stack or self._processing_input:
            return

        thread_object = self._input_stack[-1]

        thread_object.initialize_thread()
        self._processing_input = True
        thread_object.start_thread()

    def _find_running_thread_objects(self):
        ret_list = []
        for t in self._input_stack:
            if t.thread and t.thread.is_alive():
                ret_list.append(t)

        return ret_list


class InputRequest(object, metaclass=ABCMeta):
    """Base input request class.

    This should be overloaded for every InputHandler class. Purpose of this class is to print
    prompt and get input from user.

    The `run_input` method is the entry point for this class. Output from this method must be
    a user input.

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
    def get_input(self):
        """Print prompt and get an input from user.

        ..NOTE: Overload this method in your class.

        Return this input from a function.
        """
        return ""
