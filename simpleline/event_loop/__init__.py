# Abstract base class for Simpleline Event Loop.
#
# This class can be overridden to use any existing event loop of your program.
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

from abc import ABCMeta, abstractmethod
from collections import namedtuple

from simpleline.errors import SimplelineError
from simpleline.event_loop.ticket_machine import TicketMachine
from simpleline.logging import get_simpleline_logger

log = get_simpleline_logger()

__all__ = ["AbstractEventLoop", "AbstractSignal", "ExitMainLoop"]

QuitCallback = namedtuple("QuitCallback", ["callback", "args"])


class ExitMainLoop(SimplelineError):
    """This exception ends the whole event loop."""
    pass


class AbstractEventLoop(metaclass=ABCMeta):

    def __init__(self):
        super().__init__()
        self._handlers = {}
        self._processed_signals = TicketMachine()
        self._quit_callback = None
        # end most inner loop politely by setting to False
        self._run_loop = True
        self._force_quit = False

    def register_signal_handler(self, signal, callback, data=None):
        """Register a callback which will be called when message "event"
        is encountered during process_events.

        The callback has to accept two arguments:
        - the received message in the form of (type, [arguments])
        - the data registered with the handler

        :param signal: Signal class we want to react on.
        :type signal: Class based on the simpleline.event_loop.AbstractSignal class.

        :param callback: The callback function.
        :type callback: func(event_message, data)

        :param data: Optional data to pass to callback.
        :type data: Anything.
        """
        if signal not in self._handlers:
            self._handlers[signal] = []

        event_handler = self._create_event_handler(callback, data)
        self._handlers[signal].append(event_handler)

    @abstractmethod
    def register_signal_source(self, signal_source):
        """Register source of signal for actual event queue.

        :param signal_source: Source for future signals.
        :type signal_source: `simpleline.render.ui_screen.UIScreen`
        """
        pass

    @abstractmethod
    def enqueue_signal(self, signal):
        """Enqueue new event for processing.

        :param signal: Signal which you want to add to the event queue for processing.
        :type signal: Instance based on AbstractEvent class.
        """
        log.debug("New signal %s enqueued with source %s", signal, signal.source.__class__.__name__)

    @abstractmethod
    def run(self):
        """Starts the event loop."""
        log.debug("Starting main loop")
        self._force_quit = False

    def force_quit(self):
        """Force quit all running event loops.

        Kill all loop including inner loops (modal window).
        None of the Simpleline events will be processed anymore.
        """
        log.debug("Force quit called. Killing all loops!")
        self._force_quit = True

    @abstractmethod
    def execute_new_loop(self, signal):
        """Starts the new event loop and pass `signal` in it.

        This is required for processing a modal screens.

        :param signal: Signal passed to the new event loop.
        :type signal: The `AbstractSignal` based class.
        """
        log.debug("Executing inner loop")

    @abstractmethod
    def close_loop(self):
        """Close active event loop.

        Close an event loop created by the `execute_new_loop()` method.
        """
        log.debug("Closing inner loop")

    @abstractmethod
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
        pass

    def set_quit_callback(self, callback, args=None):
        """Call this callback when event loop quits.

        :param callback: Call this callback when event loops ends (application quit).
        :type callback: Function with one parameter data `func(data)`.

        :param args: Arguments passed to the quit callback.
        :type args: Anything.
        """
        self._quit_callback = QuitCallback(callback, args)

    def _create_event_handler(self, callback, data):
        """Create event handler data object and return it."""
        return EventHandler(callback=callback, data=data)

    def _register_wait_on_signal(self, wait_on_signal):
        """Register process waiting on signal `wait_on_signal` and return id for later checking.

        ID is returned which is then used in the `self._check_if_signal_processed()` method.

        :param wait_on_signal: Signal we are waiting for.
        :type wait_on_signal: Class based on `simpleline.event_loop.AbstractSignal`.
        """
        return self._processed_signals.take_ticket(wait_on_signal.__name__)

    def _mark_signal_processed(self, signal):
        """Mark that processes waiting on this signal that they are able to go.

        :param signal: Signal which was processed.
        :type signal: Class based on `simpleline.event_loop.AbstractSignal`.
        """
        self._processed_signals.mark_line_to_go(signal.__class__.__name__)

    def _check_if_signal_processed(self, wait_on_signal, unique_id):
        """Check if the signal was processed.

        :param wait_on_signal: Signal the process is waiting for.
        :type wait_on_signal: Class based on `simpleline.event_loop.AbstractSignal`.

        :param unique_id: Unique id returned by the `self._register_wait_on_signal()` method.
        :type unique_id: int
        """
        return self._processed_signals.check_ticket(wait_on_signal.__name__, unique_id)


class EventHandler(object):
    """Data class to save event handlers."""

    def __init__(self, callback, data):
        self.callback = callback
        self.data = data


class AbstractSignal(metaclass=ABCMeta):
    """This class is base class for signals.

    .. NOTE:
    Ordering and equality is based on priority.
    """

    def __init__(self, source, priority=0):
        self._source = source
        self._priority = priority

    def __lt__(self, other):
        """Order Signal classes by priority."""
        return self._priority < other.priority

    def __eq__(self, other):
        """Order Signal classes by priority."""
        return self._priority == other.priority

    def __str__(self):
        """For easier logging."""
        return self.__class__.__name__

    @property
    def priority(self):
        """Priority of this event.

        Values less than 0 denote higher priorities. Values greater than 0 denote lower priorities.
        Events from high priority sources are always processed before events from lower priority sources.
        """
        return self._priority

    @property
    def source(self):
        """Source which emitted this event."""
        return self._source
