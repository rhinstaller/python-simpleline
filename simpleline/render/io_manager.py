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


import queue
import threading
import sys
import getpass

from enum import Enum

from simpleline.render import INPUT_PROCESSED, INPUT_DISCARDED
from simpleline.event_loop import ExitMainLoop
from simpleline.event_loop.signals import ExceptionSignal, InputReadySignal
from simpleline.render.prompt import Prompt
from simpleline.render.widgets import TextWidget


RAW_INPUT_LOCK = threading.Lock()


class InOutManager(object):

    def __init__(self, event_loop):
        """Processor for common user input and output.

        :param event_loop: Event loop used for the renderer.
        :type event_loop: Class based on `simpleline.event_loop.AbstractEventLoop`.
        """
        super().__init__()
        self._input_error_counter = 0
        self._input_error_threshold = 5
        self._input_thread = None
        self._event_loop = event_loop
        self._getpass_func = getpass.getpass
        self._width = 80
        self._spacer = ""
        self._calculate_spacer()

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
            # separate the content on the screen from the stuff we are about to display now
            print(self._spacer)
            # print UIScreen content
            active_screen.ui_screen.show_all()
        except ExitMainLoop:
            raise
        except Exception:    # pylint: disable=broad-except
            self._event_loop.enqueue_signal(ExceptionSignal(self))

    def process_input(self, active_screen):
        """Process input from the screens.

        Result of the processing is saved in the `processed_result` property.

        :param active_screen: Screen demanding this input processing.
        :type active_screen: Classed based on `simpleline.render.screen.UIScreen`.

        :raises: ExitMainLoop or any other kind of exception from screen processing.

        :return: Return data object with result status and state.
        :rtype: `simpleline.render.in_out_manager.UserInputResult` class.
        """
        last_screen = active_screen.ui_screen
        # get the screen's prompt
        prompt = last_screen.prompt(active_screen.args)

        # None means prompt handled the input by itself -> continue
        if prompt is None:
            return True

        # get the input from user
        c = self.get_user_input(prompt)

        # process the input, if it wasn't processed (valid)
        # increment the error counter
        result = self._process_input(active_screen, c)
        if result.was_successful():
            self._input_error_counter = 0
        else:
            self._input_error_counter += 1
        return result

    def get_user_input(self, prompt, hidden=False):
        """This method reads one input from user. Its basic form has only one
        line, but we might need to override it for more complex apps or testing.
        """
        if self._input_thread is not None and self._input_thread.is_alive():
            raise KeyError("Can't run multiple input threads at the same time!")

        input_queue = queue.Queue()
        self._input_thread = threading.Thread(target=self._thread_input, name="InputThread",
                                              args=(input_queue, prompt, hidden))
        self._input_thread.daemon = True
        self._input_thread.start()
        self._event_loop.process_signals(return_after=InputReadySignal)
        return input_queue.get()  # return the user input

    def _thread_input(self, queue_instance, prompt, hidden):
        """This method is responsible for interruptable user input.

        It is expected to be used in a thread started on demand
        and returns the input via the communication Queue.

        :param queue_instance: communication queue_instance to be used
        :type queue_instance: queue.Queue instance

        :param prompt: prompt to be displayed
        :type prompt: Prompt instance

        :param hidden: whether typed characters should be echoed or not
        :type hidden: bool
        """
        if hidden:
            data = self._getpass_func(prompt)
        else:
            widget = TextWidget(str(prompt))
            widget.render(self._width)
            lines = widget.get_lines()
            sys.stdout.write("\n".join(lines) + " ")
            sys.stdout.flush()
            if not RAW_INPUT_LOCK.acquire(False):
                # raw_input is already running
                return
            else:
                # lock acquired, we can run input
                try:
                    data = self._get_input()
                except EOFError:
                    data = ""
                finally:
                    RAW_INPUT_LOCK.release()

        self._event_loop.enqueue_signal(InputReadySignal(self))
        queue_instance.put(data)

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
        """
        # delegate the handling to active screen first
        try:
            key = active_screen.ui_screen.input(active_screen.args, key)
            if key == INPUT_PROCESSED:
                return UserInputResult.PROCESSED
            elif key == INPUT_DISCARDED:
                return UserInputResult.ERROR
        except ExitMainLoop:
            raise
        except Exception:    # pylint: disable=broad-except
            self._event_loop.enqueue_signal(ExceptionSignal(self))
            return UserInputResult.ERROR

        # global refresh command
        if key == Prompt.REFRESH:
            return UserInputResult.REFRESH

        # global close command
        if key == Prompt.CONTINUE:
            return UserInputResult.CONTINUE

        # global quit command
        if key == Prompt.QUIT:
            return UserInputResult.QUIT

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
