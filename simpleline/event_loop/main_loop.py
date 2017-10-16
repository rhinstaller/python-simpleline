# Default event loop for Simpleline application.
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

from threading import Lock

from simpleline.event_loop import AbstractEventLoop, ExitMainLoop
from simpleline.event_loop.event_queue import EventQueue
from simpleline.event_loop.signals import ExceptionSignal
from simpleline.logging import get_simpleline_logger

log = get_simpleline_logger()

__all__ = ["MainLoop"]


class MainLoop(AbstractEventLoop):
    """Default main event loop for the Simpleline.

    This event loop can be replaced by your event loop by implementing `simpleline.event_loop.AbstractEventLoop` class.
    """

    def __init__(self):
        super().__init__()
        self._active_queue = EventQueue()
        self._event_queues = [self._active_queue]
        self._lock = Lock()

    def register_signal_source(self, signal_source):
        """Register source of signal for actual event queue.

        :param signal_source: Source for future signals.
        :type signal_source: `simpleline.render.ui_screen.UIScreen`.
        """
        super().register_signal_source(signal_source)
        self._active_queue.add_source(signal_source)

    def run(self):
        """This methods starts the application.

        Do not use self.mainloop() directly as run() handles all the required exceptions
        needed to keep nested mainloop working.
        """
        super().run()
        self._run_loop = True

        try:
            self._mainloop()
        except ExitMainLoop:
            pass

        log.debug("Main loop ended. Running callback if set.")

        if self._quit_callback:
            cb = self._quit_callback.callback
            cb(self._quit_callback.args)

    def force_quit(self):
        """Force quit all running event loops.

        Kill all loop including inner loops (modal window).
        None of the Simpleline events will be processed anymore.
        """
        super().force_quit()
        self._event_queues.clear()
        self._run_loop = False

    def execute_new_loop(self, signal):
        """Starts the new event loop and pass `signal` in it.

        This is required for processing a modal screens.

        :param signal: Signal passed to the new event loop.
        :type signal: The `AbstractSignal` based class.
        """
        super().execute_new_loop(signal)

        if self._force_quit:
            return

        self._active_queue = EventQueue()

        # TODO: Remove when python3-astroid 1.5.3 will be in Fedora
        # pylint: disable=not-context-manager
        with self._lock:
            self._event_queues.append(self._active_queue)

        self.enqueue_signal(signal)
        self._mainloop()
        log.debug("Inner loop is closed")

    def close_loop(self):
        """Close active event loop.

        Close an event loop created by the `execute_new_loop()` method.
        """
        super().close_loop()
        self.process_signals()

        # TODO: Remove when python3-astroid 1.5.3 will be in Fedora
        # pylint: disable=not-context-manager
        with self._lock:
            self._event_queues.pop()
            try:
                self._active_queue = self._event_queues[-1]
            except IndexError:
                log.error("No more event queues to work with!")
                raise ExitMainLoop()

        self._run_loop = False

    def enqueue_signal(self, signal):
        """Enqueue new event for processing.

        Enqueue signal to the most inner queue (nearest to the active queue) where the `signal.source` belongs.
        If it belongs nowhere enqueue it to the active one.

        This method is thread safe.

        :param signal: Event which you want to add to the event queue for processing.
        :type signal: Instance based on AbstractEvent class.
        """
        if self._force_quit:
            return

        super().enqueue_signal(signal)
        # TODO: Remove when python3-astroid 1.5.3 will be in Fedora
        # pylint: disable=not-context-manager
        with self._lock:
            for queue in reversed(self._event_queues):
                if queue.enqueue_if_source_belongs(signal, signal.source):
                    return

        self._active_queue.enqueue(signal)

    def _mainloop(self):
        """Single mainloop. Do not use directly, start the application using run()."""
        # run infinite loop
        # this will always wait on input processing or similar so it should not busy waiting
        while self._run_loop:
            self._process_signals_loop()

        if not self._force_quit:
            # set back to True to leave outer loop working
            self._run_loop = True

    def process_signals(self, return_after=None):
        """This method processes incoming async messages.

        Process signals enqueued by the `self.enqueue_signal()` method. Call handlers registered to the signals by
        the `self.register_signal_handler()` method.

        When `return_after` is specified then wait to the point when this signal is processed.
        NO warranty that this method will return immediately after the signal was processed!

        Without `return_after` parameter this method will return after all queued signals with the highest priority
        will be processed.

        The method is NOT thread safe!

        :param return_after: Wait on this signal to be processed.
        :type return_after: Class of the signal.
        """
        super().process_signals(return_after)
        if return_after is not None:
            self._process_signals_with_return(return_after)
        else:
            self._process_signals_iteration()

    def _process_signals_with_return(self, return_after):
        """Process signals until the return_after signal was processed.

        Or the loop quited.
        """
        # get unique ID when waiting for the signal
        unique_id = self._register_wait_on_signal(return_after)

        while self._run_loop:
            signal = self._active_queue.get()

            # do the signal processing (call handlers)
            self._process_signal(signal)

            # was our signal processed if yes, return this method
            if self._check_if_signal_processed(return_after, unique_id):
                return

    def _process_signals_iteration(self):
        """Process queued signal and then return."""
        priority = None

        while not self._active_queue.empty() and self._run_loop:
            if priority is None:
                # take first signal to find out the highest priority in queue
                signal = self._active_queue.get()
                priority = signal.priority
            else:
                # get signal with this priority only
                signal = self._active_queue.get_top_event_if_priority(priority)

            # Signal with this priority is not available anymore
            if signal is None:
                return

            self._process_signal(signal)

    def _process_signals_loop(self):
        """Process signal until the event loop quited."""
        while self._run_loop:
            signal = self._active_queue.get()
            self._process_signal(signal)

    def _process_signal(self, signal):
        log.debug("Processing signal %s", signal)

        self._mark_signal_processed(signal)

        if type(signal) in self._handlers:
            for handler_data in self._handlers[type(signal)]:
                try:
                    handler_data.callback(signal, handler_data.data)
                except ExitMainLoop:
                    raise
                except Exception:  # pylint: disable=broad-except
                    self.enqueue_signal(ExceptionSignal(self))
        elif type(signal) is ExceptionSignal:
            self.kill_app_with_traceback(signal)
