# Default event queue for Simpleline application.
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
from simpleline import SimplelineError


class EventQueueError(SimplelineError):
    pass


# TODO: Document this
class EventQueue(object):

    def __init__(self):
        self._queue = PriorityQueue()
        self._contained_screens = set()

    def empty(self):
        return self._queue.empty()

    def enqueue(self, signal):
        self._queue.put(signal)

    def enqueue_if_source_belongs(self, signal, source):
        if self.contains_source(source):
            self._queue.put(signal)
            return True
        else:
            return False

    def get(self):
        return self._queue.get()

    def add_source(self, signal_source):
        self._contained_screens.add(signal_source)

    def remove_source(self, signal_source):
        try:
            self._contained_screens.remove(signal_source)
        except KeyError:
            raise EventQueueError("Can't remove non-existing event source!")

    def contains_source(self, signal_source):
        return signal_source in self._contained_screens
