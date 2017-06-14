# Class handling rendering of the screens to console.
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

import getpass
import queue
import sys
import threading

from simpleline.event_loop import ExitMainLoop, ExitAllMainLoops
from simpleline.event_loop.signals import ExceptionSignal, InputReadySignal
from simpleline.render import RendererUnexpectedError
from simpleline.render.prompt import Prompt
from simpleline.render.widgets import TextWidget
from simpleline.screen_stack import ScreenStack, ScreenData, ScreenStackEmptyException

RAW_INPUT_LOCK = threading.Lock()


class Renderer(object):

    def __init__(self, event_loop, renderer_stack=None, width=80):
        """Constructor where you can pass your own renderer stack.

        The ScreenStack will be used automatically if renderer stack will be None.

        :param event_loop: Event loop used for the renderer.
        :type event_loop: Class based on `simpleline.event_loop.AbstractEventLoop`.
        :param renderer_stack: Input your own renderer stack if you need to.
        :type renderer_stack: `simpleline.screen_stack.ScreenStack` based class.
        :param width: Width of the screen
        :type width: unsigned int in range <0;screen size>
        """
        self._quit_screen = None
        self._quit_message = ""
        self._event_loop = event_loop
        self._redraw = True
        self._spacer = "\n".join(2 * [width * "="])
        self._width = width
        self._input_error_counter = 0
        self._input_thread = None
        if renderer_stack:
            self._screen_stack = renderer_stack
        else:
            self._screen_stack = ScreenStack()

    @property
    def width(self):
        return self._width

    @property
    def quit_screen(self):
        return self._quit_screen

    @quit_screen.setter
    def quit_screen(self, quit_screen):
        self._quit_screen = quit_screen

    @property
    def quit_message(self):
        """This message will be send to quit_screen."""
        return self._quit_message

    @quit_message.setter
    def quit_message(self, msg):
        """This message will be send to quit_screen."""
        self._quit_message = msg

    def nothing_to_render(self):
        """Is something for rendering in the renderer stack?

        :return: True if the rendering stack is empty
        :rtype: bool
        """
        return self._screen_stack.is_empty()

    def schedule_screen(self, ui_screen, args=None):
        """Add screen to the bottom of the stack.

        This is mostly useful at the beginning to prepare the first screen hierarchy to display.

        :param ui_screen: screen to show
        :type ui_screen: UIScreen instance
        :param args: optional argument, please see switch_screen for details
        :type args: anything
        """
        screen = ScreenData(ui_screen, args)
        self._screen_stack.add_first(screen)

    def replace_screen(self, ui, args=None):
        """Schedules a screen to replace the current one.

        :param ui: screen to show
        :type ui: instance of UIScreen
        :param args: optional argument to pass to ui's refresh and setup methods
                     (can be used to select what item should be displayed or so)
        :type args: anything
        """
        try:
            old_loop = self._screen_stack.pop().execute_loop
        except ScreenStackEmptyException:
            raise ScreenStackEmptyException("Switch screen is not possible when there is no screen scheduled!")

        # we have to keep the old_loop value so we stop
        # dialog's mainloop if it ever uses switch_screen
        screen = ScreenData(ui, args, old_loop)
        self._screen_stack.append(screen)
        self.redraw()

    def switch_screen(self, ui, args=None):
        """Schedules a screen to show, but keeps the current one in stack to
        return to, when the new one is closed.

        :param ui: screen to show
        :type ui: UIScreen instance
        :param args: optional argument, please see switch_screen for details
        :type args: anything
        """
        screen = ScreenData(ui, args, False)
        self._screen_stack.append(screen)
        self.redraw()

    def switch_screen_modal(self, ui, args=None):
        """Starts a new screen right away, so the caller can collect data back.

        When the new screen is closed, the caller is redisplayed.

        This method does not return until the new screen is closed.

        :param ui: screen to show
        :type ui: UIScreen instance
        :param args: optional argument, please see switch_screen for details
        :type args: anything
        """
        screen = ScreenData(ui, args, True)
        self._screen_stack.append(screen)
        self._do_redraw()

    def close_screen(self):
        """Close the currently displayed screen and exit it's main loop if necessary.

        Next screen from the stack is then displayed.
        """
        screen = self._screen_stack.pop()

        # User can react when screen is closing
        screen.ui_screen.closed()

        # this cannot happen, if we are closing the window,
        # the loop must have been running or not be there at all
        if screen.execute_loop:
            raise RendererUnexpectedError("New main loop is requested when closing window!")

        # we are in modal window, end it's loop
        if screen.end_loop:
            raise ExitMainLoop()

        if not self._screen_stack.is_empty():
            self.redraw()
        else:
            raise ExitMainLoop()

    def redraw(self):
        """Set the redraw flag so the screen is refreshed as soon as possible."""
        self._redraw = True

    def _do_redraw(self):
        """Draws the current screen and returns True if user input is requested.

        If modal screen is requested, starts a new loop and initiates redraw after it ends.
        """
        if self._screen_stack.is_empty():
            raise ExitMainLoop()

        top_screen = self._screen_stack.pop(False)

        # this screen is used first time (call setup() method)
        if not top_screen.ui_screen.ready:
            if not top_screen.ui_screen.setup(top_screen.args):
                # skip if setup went wrong
                return

        # new mainloop is requested
        if top_screen.execute_loop:
            # change the record to indicate mainloop is running
            self._screen_stack.pop()
            self.switch_screen(top_screen.ui_screen, top_screen.args)
            # notify that this loop should be ended
            top_screen.end_loop = True
            # start the mainloop
            self._event_loop.execute_new_loop()
            # after the mainloop ends, set the redraw flag
            # and skip the input processing once, to redisplay the screen first
            self.redraw()
            input_needed = False
        elif self._redraw:
            # if redraw is needed, separate the content on the screen from the
            # stuff we are about to display now
            self._input_error_counter = 0
            print(self._spacer)

            # get the widget tree from the screen and show it in the screen
            try:
                input_needed = top_screen.ui_screen.refresh(top_screen.args)
                top_screen.ui_screen.show_all()
                self._redraw = False
            except ExitMainLoop:
                raise
            except Exception:    # pylint: disable=broad-except
                self._event_loop.enqueue_signal(ExceptionSignal(self))
                return False

        else:
            # this can happen only in case there was invalid input and prompt
            # should be shown again
            input_needed = True

        if input_needed:
            self._process_input()

    def _process_input(self):
        active_screen = self._screen_stack.pop(remove=False)
        last_screen = active_screen.ui_screen
        # get the screen's prompt
        try:
            prompt = last_screen.prompt(active_screen.args)
        except ExitMainLoop:
            raise
        except Exception:    # pylint: disable=broad-except
            self._event_loop.enqueue_signal(ExceptionSignal(self))
            return

        # None means prompt handled the input by itself
        # ask for redraw and continue
        if prompt is None:
            self.redraw()
            return

        # get the input from user
        c = self.raw_input(prompt)

        # process the input, if it wasn't processed (valid)
        # increment the error counter
        if not self.input(active_screen.args, c):
            self._input_error_counter += 1
        else:
            # input was successfully processed, but no other screen was
            # scheduled, just redraw the screen to display current state
            self.redraw()

        # redraw the screen after 5 bad inputs
        if self._input_error_counter >= 5:
            self.redraw()

    def raw_input(self, prompt, hidden=False):
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
        self._event_loop.process_events(return_after=InputReadySignal)
        return input_queue.get()  # return the user input

    def input(self, args, key):
        """Method called internally to process unhandled input key presses.

        Also handles the main quit and close commands.

        :param args: optional argument passed from switch_screen calls
        :type args: anything

        :param key: the string entered by user
        :type key: str

        :return: True if key was processed, False if it was not recognized
        :rtype: True|False
        """
        # delegate the handling to active screen first
        if not self._screen_stack.is_empty():
            try:
                key = self._screen_stack.pop(False).ui_screen.input(args, key)
                if key is None:
                    return True
            except ExitMainLoop:
                raise
            except Exception:    # pylint: disable=broad-except
                self._event_loop.enqueue_signal(ExceptionSignal(self))
                return False

        # global refresh command
        if not self._screen_stack.is_empty() and (key == Prompt.REFRESH):
            self._do_redraw()
            return True

        # global close command
        if not self._screen_stack.is_empty() and (key == Prompt.CONTINUE):
            self.close_screen()
            return True

        # global quit command
        elif not self._screen_stack.is_empty() and (key == Prompt.QUIT):
            if self._quit_screen:
                d = self.quit_screen(self, self._quit_message)
                self.switch_screen_modal(d)
                if d.answer:
                    raise ExitAllMainLoops()
            else:
                raise ExitAllMainLoops()
            return True

        return False

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
            data = getpass.getpass(prompt)
        else:
            widget = TextWidget(str(prompt))
            widget.render(self._width)
            lines = widget.get_lines()
            sys.stdout.write("\n".join(lines) + " ")
            sys.stdout.flush()
            # XXX: only one raw_input can run at a time, don't schedule another
            # one as it would cause weird behaviour and block other packages'
            # raw_inputs
            if not RAW_INPUT_LOCK.acquire(False):
                # raw_input is already running
                return
            else:
                # lock acquired, we can run raw_input
                try:
                    data = input()
                except EOFError:
                    data = ""
                finally:
                    RAW_INPUT_LOCK.release()

        queue_instance.put(data)
