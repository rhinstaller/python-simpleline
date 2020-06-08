# Default event queue for Simpleline application.
#
# This class is thread safe.
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
# Author(s): Jiri Konecny <jkonecny@redhat.com>
#


from queue import PriorityQueue
from threading import Lock

from simpleline.errors import SimplelineError


class EventQueueError(SimplelineError):
    """Main exception for `EventQueue` class.

    Inherits from `simpleline.SimplelineError`.
    """


class EventQueue(object):
    """Class for managing signal queue.

    Responsibilities of this class are:
    * sorting by priority of signals
    * managing sources for this event queue
    * enqueuing signals
    """

    def __init__(self):
        self._queue = PriorityQueue()
        self._contained_screens = set()
        self._lock = Lock()

    def empty(self):
        """Return true if Queue is empty.

        :return: True if empty, False otherwise.
        """
        return self._queue.empty()

    def enqueue(self, signal):
        """Enqueue signal to this queue.

        :param signal: Signal which should be enqueued to this queue.
        :type signal: Signal class based on `simpleline.event_loop.signals.AbstractSignal`.
        """
        self._queue.put(signal)

    def enqueue_if_source_belongs(self, signal, source):
        """Enqueue signal to this queue if the signal source belongs to this queue.

        Enqueue the `signal` only if the `source` belongs to this queue. See the `add_source()` method.

        :param signal: Signal which should be enqueued to this queue.
        :type signal: Signal class based on `simpleline.event_loop.signals.AbstractSignal`.
        :param source: Source of this signal.
        :type source: Anything.
        :return: True if the source belongs to this queue and signal was queued, False otherwise.
        :rtype: bool
        """
        if self.contains_source(source):
            self._queue.put(signal)
            return True
        else:
            return False

    def get(self):
        """Return enqueued signal with the highest priority.

        This is FIFO implementation for the same priority.
        If the queue is empty this method will wait for the input signal.

        :return: Queued signal.
        :rtype: Signal based on class `simpleline.event_loop.signals.AbstractSignal`.
        """
        return self._queue.get()

    def get_top_event_if_priority(self, priority):
        """Return top enqueued signal if priority is equal to `priority`. Otherwise `None`.

        :param priority: Requested event priority.
        :type priority: int

        :return: Queued signal if it has requested priority. Otherwise `None`.
        :rtype: Signal based on class `simpleline.event_loop.signals.AbstractSignal` or `None`.
        """
        event = self._queue.get()
        if event.priority == priority:
            return event
        else:
            self._queue.put(event)
            return None

    def add_source(self, signal_source):
        """Add new source of signals to this queue.

        This method is mandatory for `enqueue_if_source_belongs()` method.
        The same source will be added only once.

        :param signal_source: Source of future signals.
        :type signal_source: Anything which will emit signals in future.
        """
        # TODO: Remove when python3-astroid 1.5.3 will be in Fedora
        # pylint: disable=not-context-manager
        with self._lock:
            self._contained_screens.add(signal_source)

    def remove_source(self, signal_source):
        """Remove signal source from this queue.

        :param signal_source: Source of future signals.
        :type signal_source: Anything.
        :raise: EventQueueError"""
        try:
            # TODO: Remove when python3-astroid 1.5.3 will be in Fedora
            # pylint: disable=not-context-manager
            with self._lock:
                self._contained_screens.remove(signal_source)
        except KeyError:
            raise EventQueueError("Can't remove non-existing event source!")

    def contains_source(self, signal_source):
        """Test if `signal_source` belongs to this queue.

        :param signal_source: Source of signals.
        :type signal_source: Anything.
        :return: True if signal source belongs to this queue.
        :rtype: bool
        """
        # TODO: Remove when python3-astroid 1.5.3 will be in Fedora
        # pylint: disable=not-context-manager
        with self._lock:
            return signal_source in self._contained_screens
