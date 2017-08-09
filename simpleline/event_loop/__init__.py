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
from simpleline.errors import SimplelineError


class ExitMainLoop(SimplelineError):
    """This exception ends the whole event loop."""
    pass


class AbstractEventLoop(metaclass=ABCMeta):

    def __init__(self):
        self._quit_callback = None
        super().__init__()

    @abstractmethod
    def register_signal_handler(self, signal, callback, data=None):
        """Register a callback which will be called when message "event"
        is encountered during process_events.

        The callback has to accept two arguments:
        - the received message in the form of (type, [arguments])
        - the data registered with the handler

        :param signal: signal class we want to react on
        :type signal: class based on the simpleline.event_loop.AbstractSignal class

        :param callback: the callback function
        :type callback: func(event_message, data)

        :param data: optional data to pass to callback
        :type data: anything
        """
        pass

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

        :param signal: signal which you want to add to the event queue for processing
        :type signal: instance based on AbstractEvent class
        """
        pass

    @abstractmethod
    def run(self):
        """Starts the event loop."""
        pass

    @abstractmethod
    def execute_new_loop(self, signal):
        """Starts the new event loop and pass `signal` in it.

        This is required for processing a modal screens.

        :param signal: signal passed to the new event loop
        :type signal: `AbstractSignal` based class
        """
        pass

    @abstractmethod
    def close_loop(self):
        """Close active event loop.

        Close an event loop created by the `execute_new_loop()` method.
        """
        pass

    @abstractmethod
    def process_signals(self, return_after=None):
        """This method processes incoming async messages.

        Process signals enqueued by the `self.enqueue_signal()` method. Call handlers registered to the signals by
        the `self.register_signal_handler()` method.

        When `return_after` is specified then wait to the point when this signal is processed. This could be after
        some more signals was processed because of recursion in calls.
        Without `return_after` parameter this method will return after all queued signals will be processed.

        The method is NOT thread safe!

        :param return_after: Wait on this signal to be processed.
        :type return_after: Class of the signal.
        """
        pass

    def event_loop_quit_callback(self, callback):
        """Call this callback when event loop quits."""
        self._quit_callback = callback


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
