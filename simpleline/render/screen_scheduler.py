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

import threading


from simpleline import App
from simpleline.event_loop import ExitMainLoop
from simpleline.event_loop.signals import ExceptionSignal, RenderScreenSignal, CloseScreenSignal
from simpleline.render import RenderUnexpectedError
from simpleline.render.screen.input_manager import UserInputAction
from simpleline.render.screen_stack import ScreenStack, ScreenData, ScreenStackEmptyException

from simpleline.logging import get_simpleline_logger

log = get_simpleline_logger()

RAW_INPUT_LOCK = threading.Lock()


__all__ = ["ScreenScheduler"]


class ScreenScheduler(object):

    def __init__(self, event_loop, scheduler_stack=None):
        """Constructor where you can pass your own scheduler stack.

        The ScreenStack will be used automatically if scheduler stack will be None.

        :param event_loop: Event loop used for the scheduler.
        :type event_loop: Class based on `simpleline.event_loop.AbstractEventLoop`.
        :param scheduler_stack: Use custom scheduler stack if you need to.
        :type scheduler_stack: `simpleline.screen_stack.ScreenStack` based class.
        """
        self._quit_screen = None
        self._event_loop = event_loop

        if scheduler_stack:
            self._screen_stack = scheduler_stack
        else:
            self._screen_stack = ScreenStack()
        self._register_handlers()

        self._first_screen_scheduled = False

    def _spacer(self):
        return "\n".join(2 * [App.get_width() * "="])

    def _register_handlers(self):
        self._event_loop.register_signal_handler(RenderScreenSignal, self._process_screen_callback)
        self._event_loop.register_signal_handler(CloseScreenSignal, self._close_screen_callback)

    @property
    def quit_screen(self):
        """Return quit UIScreen."""
        return self._quit_screen

    @quit_screen.setter
    def quit_screen(self, quit_screen):
        """Set the UIScreen based instance which will be showed before the Application will quit.

        You can also use `simpleline.render.adv_widgets.YesNoDialog` or `UIScreen` based class
        with the `answer` property. Without the `answer` property the application will always
        close.
        """
        self._quit_screen = quit_screen

    @property
    def nothing_to_render(self):
        """Is something for rendering in the scheduler stack?

        :return: True if the rendering stack is empty
        :rtype: bool
        """
        return self._screen_stack.empty()

    def dump_stack(self):
        """Get string representation of actual screen stack."""
        return self._screen_stack.dump_stack()

    def schedule_screen(self, ui_screen, args=None):
        """Add screen to the bottom of the stack.

        This is mostly useful at the beginning to prepare the first screen hierarchy to display.

        :param ui_screen: screen to show
        :type ui_screen: UIScreen instance
        :param args: optional argument, please see switch_screen for details
        :type args: anything
        """
        log.debug("Scheduling screen %s", ui_screen)
        screen = ScreenData(ui_screen, args)
        self._screen_stack.add_first(screen)
        self._redraw_on_first_scheduled_screen()

    def _redraw_on_first_scheduled_screen(self):
        if not self._first_screen_scheduled:
            self.redraw()
            self._first_screen_scheduled = True

    def replace_screen(self, ui_screen, args=None):
        """Schedules a screen to replace the current one.

        :param ui_screen: screen to show
        :type ui_screen: instance of UIScreen
        :param args: optional argument to pass to ui's refresh and setup methods
                     (can be used to select what item should be displayed or so)
        :type args: anything
        """
        log.debug("Replacing screen %s", ui_screen)
        try:
            execute_new_loop = self._screen_stack.pop().execute_new_loop
        except ScreenStackEmptyException:
            raise ScreenStackEmptyException("Switch screen is not possible when there is no "
                                            "screen scheduled!")

        # we have to keep the old_loop value so we stop
        # dialog's mainloop if it ever uses switch_screen
        screen = ScreenData(ui_screen, args, execute_new_loop)
        self._screen_stack.append(screen)
        self.redraw()

    def push_screen(self, ui_screen, args=None):
        """Schedules a screen to show, but keeps the current one in stack to
        return to, when the new one is closed.

        :param ui_screen: screen to show
        :type ui_screen: UIScreen instance
        :param args: optional argument
        :type args: anything
        """
        log.debug("Pushing screen %s to stack", ui_screen)
        screen = ScreenData(ui_screen, args, False)
        self._screen_stack.append(screen)
        self.redraw()

    def push_screen_modal(self, ui_screen, args=None):
        """Starts a new screen right away, so the caller can collect data back.

        When the new screen is closed, the caller is redisplayed.

        This method does not return until the new screen is closed.

        :param ui_screen: screen to show
        :type ui_screen: UIScreen instance
        :param args: optional argument, please see switch_screen for details
        :type args: anything
        """
        log.debug("Pushing modal screen %s to stack", ui_screen)
        screen = ScreenData(ui_screen, args, True)
        self._screen_stack.append(screen)
        # only new events will be processed now
        # the old one will wait after this event loop will be closed
        self._event_loop.execute_new_loop(RenderScreenSignal(self))

    def _close_screen_callback(self, signal, data):
        self.close_screen(signal.source)

    def close_screen(self, closed_from=None):
        """Close the currently displayed screen and exit it's main loop if necessary.

        Next screen from the stack is then displayed.
        """
        screen = self._screen_stack.pop()
        log.debug("Closing screen %s from %s", screen, closed_from)

        # User can react when screen is closing
        screen.ui_screen.closed()

        if closed_from is not None and closed_from is not screen.ui_screen:
            raise RenderUnexpectedError("You are trying to close screen %s from screen %s! "
                                        "This is most probably not intentional." %
                                        (closed_from, screen.ui_screen))

        if screen.execute_new_loop:
            self._event_loop.close_loop()

        # redraw screen if there is what to redraw
        # and if it is not modal screen (modal screen parent is blocked)
        if not self._screen_stack.empty() and not screen.execute_new_loop:
            self.redraw()

        # we can't draw anything more. Kill the application.
        if self._screen_stack.empty():
            raise ExitMainLoop()

    def redraw(self):
        """Register rendering to the event loop for processing."""
        self._event_loop.enqueue_signal(RenderScreenSignal(self))

    def _process_screen_callback(self, signal, data):
        self._process_screen()

    def _process_screen(self):
        """Draws the current screen and returns True if user input is requested.

        If modal screen is requested, starts a new loop and initiates redraw after it ends.
        """
        top_screen = self._get_last_screen()

        log.debug("Processing screen %s", top_screen)

        # this screen is used first time (call setup() method)
        if not top_screen.ui_screen.screen_ready:
            if not top_screen.ui_screen.setup(top_screen.args):
                # remove the screen and skip if setup went wrong
                self._screen_stack.pop()
                self.redraw()
                log.warning("Screen %s setup wasn't successful", top_screen)
                return

        # get the widget tree from the screen and show it in the screen
        try:
            # refresh screen content
            top_screen.ui_screen.refresh(top_screen.args)

            # Screen was closed in the refresh method
            if top_screen != self._get_last_screen():
                return

            # draw screen to the console
            self._draw_screen(top_screen)

            if top_screen.ui_screen.input_required:
                log.debug("Input is required by %s screen", top_screen)
                top_screen.ui_screen.get_input_with_error_check(top_screen.args)
        except ExitMainLoop:
            raise
        except Exception:    # pylint: disable=broad-except
            self._event_loop.enqueue_signal(ExceptionSignal(self))
            return False

    def _draw_screen(self, active_screen):
        """Draws the current `active_screen`.

        :param active_screen: Screen which should be draw to the console.
        :type active_screen: Classed based on `simpleline.render.screen.UIScreen`.
        """
        # get the widget tree from the screen and show it in the screen
        try:
            if not active_screen.ui_screen.no_separator:
                # separate the content on the screen from the stuff we are about to display now
                print(self._spacer())

            # print UIScreen content
            active_screen.ui_screen.show_all()
        except ExitMainLoop:
            raise
        except Exception:    # pylint: disable=broad-except
            self._event_loop.enqueue_signal(ExceptionSignal(self))

    def _get_last_screen(self):
        if self._screen_stack.empty():
            raise ExitMainLoop()

        return self._screen_stack.pop(False)

    def process_input_result(self, input_result, should_redraw):
        active_screen = self._get_last_screen()

        if not input_result.was_successful():
            if should_redraw:
                self.redraw()
            else:
                log.debug("Input was not successful, ask for new input.")
                active_screen.ui_screen.get_input_with_error_check(active_screen.args)
        else:
            if input_result == UserInputAction.NOOP:
                return
            elif input_result == UserInputAction.REDRAW:
                self.redraw()
            elif input_result == UserInputAction.CLOSE:
                self.close_screen()
            elif input_result == UserInputAction.QUIT:
                if self.quit_screen:
                    self.push_screen_modal(self.quit_screen)
                    try:
                        if self.quit_screen.answer is True:
                            raise ExitMainLoop()
                        else:
                            self.redraw()
                    except AttributeError:
                        raise ExitMainLoop()
                else:
                    raise ExitMainLoop()
