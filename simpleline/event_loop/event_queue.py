# Default event queue for Simpleline application.
#
# This class is thread safe.
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


from queue import PriorityQueue
from threading import Lock

from simpleline.errors import SimplelineError


class EventQueueError(SimplelineError):
    """Main exception for `EventQueue` class.

    Inherits from `simpleline.SimplelineError`.
    """
    pass


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
