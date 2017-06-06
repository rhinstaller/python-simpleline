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

from abc import ABCMeta, abstractmethod, abstractclassmethod


class ExitMainLoop(Exception):
    """This exception ends the outermost mainloop. Used internally when dialogs close."""
    pass


class ExitAllMainLoops(ExitMainLoop):
    """This exception ends the whole App mainloop structure.

    App.run() returns False after the exception is processed.
    """
    pass


class AbstractEventLoop(metaclass=ABCMeta):

    @abstractmethod
    def register_event_handler(self, event, callback, data=None):
        """Register a callback which will be called when message "event"
        is encountered during process_events.

        The callback has to accept two arguments:
        - the received message in the form of (type, [arguments])
        - the data registered with the handler

        :param event: the id of the event we want to react on
        :type event: number|string

        :param callback: the callback function
        :type callback: func(event_message, data)

        :param data: optional data to pass to callback
        :type data: anything
        """
        pass

    @abstractmethod
    def enqueue_event(self, event):
        """Enqueue new event for processing.

        :param event: event which you want to add to the event queue for processing
        :type event: instance based on AbstractEvent class
        """
        pass

    @abstractmethod
    def run(self):
        """Starts the event loop."""
        pass

    @abstractmethod
    def process_events(self, return_at=None):
        """Processes incoming async messages and returns when a specific message is encountered
        or when the queue_instance is empty.

        :param return_at: If return_at message was specified, the received message is returned.
        :type return_at: Value returned by `Event.id`.

        If the message does not fit return_at, but handlers are defined then it processes all handlers for
        this message.
        """
        pass


class AbstractEvent(metaclass=ABCMeta):
    """This class is base Event class.

    You need to implement `id` property which contains event ID.
    """

    @classmethod
    @abstractclassmethod
    def id(cls):
        """This is main identifier of the Event.

        The event.id must be unique.
        """
        return "EventName"

    @property
    def priority(self):
        """Priority in the event queue.

        Values less than 0 denote higher priorities. Values greater than 0 denote lower priorities.
        Events from high priority sources are always processed before events from lower priority sources.
        """
        return 0
