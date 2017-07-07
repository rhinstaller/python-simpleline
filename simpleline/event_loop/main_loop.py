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

from simpleline.event_loop import AbstractEventLoop, ExitMainLoop
from simpleline.event_loop.signals import ExceptionSignal
from simpleline.event_loop.event_queue import EventQueue


class MainLoop(AbstractEventLoop):
    """Default main event loop for the Simpleline.

    This event loop can be replaced by your event loop by implementing `simpleline.event_loop.AbstractEventLoop` class.
    """

    def __init__(self):
        super().__init__()
        self._handlers = {}
        self._active_queue = EventQueue()
        self._event_queues = [self._active_queue]
        # handle all exceptions in the _raised_exception() method
        self.register_signal_handler(ExceptionSignal, self._raise_exception)

    def register_signal_handler(self, signal, callback, data=None):
        """Register a callback which will be called when message "event"
        is encountered during process_events.

        The callback has to accept two arguments:
        - the received message in the form of (type, [arguments])
        - the data registered with the handler

        :param signal: signal we want to react on
        :type signal: class of the signal class

        :param callback: the callback function
        :type callback: func(signal, data)

        :param data: optional data to pass to callback
        :type data: anything
        """
        if signal not in self._handlers:
            self._handlers[signal] = []
        self._handlers[signal].append(EventHandler(callback, data))

    def register_signal_source(self, signal_source):
        """Register source of signal for actual event queue.

        :param signal_source: Source for future signals.
        :type signal_source: `simpleline.render.ui_screen.UIScreen`
        """
        self._active_queue.add_source(signal_source)

    def run(self):
        """This methods starts the application.

        Do not use self.mainloop() directly as run() handles all the required exceptions
        needed to keep nested mainloop working.
        """
        self._mainloop()
        if self._quit_callback:
            self._quit_callback()

    def execute_new_loop(self, signal):
        """Starts the new event loop and pass `signal` in it.

        This is required for processing a modal screens.

        :param signal: signal passed to the new event loop
        :type signal: `AbstractSignal` based class
        """
        self._active_queue = EventQueue()
        self._event_queues.append(self._active_queue)
        self.enqueue_signal(signal)
        self._mainloop()

    def close_loop(self):
        """Close active event loop.

        Close an event loop created by the `execute_new_loop()` method.
        """
        self.process_signals()
        self._event_queues.pop()
        try:
            self._active_queue = self._event_queues[-1]
        except IndexError:
            raise ExitMainLoop()

        raise ExitMainLoop()

    def enqueue_signal(self, signal):
        """Enqueue new event for processing.

        Enqueue signal to the most inner queue (nearest to the active queue) where the `signal.source` belongs.
        If it belongs nowhere enqueue it to the active one.

        :param signal: event which you want to add to the event queue for processing
        :type signal: instance based on AbstractEvent class
        """
        for queue in reversed(self._event_queues):
            if queue.enqueue_if_source_belongs(signal, signal.source):
                return
        self._active_queue.enqueue(signal)

    def _mainloop(self):
        """Single mainloop. Do not use directly, start the application using run()."""
        # run infinite loop
        # this will always wait on input processing or similar so it is not busy waiting
        while True:
            try:
                self.process_signals()
            # end just this loop
            except ExitMainLoop:
                break

    def process_signals(self, return_after=None):
        """This method processes incoming async messages and returns
        when a specific message is processed or when the queue_instance
        is empty.

        :param return_after: return after the signal was processed
        :type return_after: class of the signal we are waiting for
        """
        while not self._active_queue.empty():
            signal = self._active_queue.get()
            if type(signal) in self._handlers:
                for handler_data in self._handlers[type(signal)]:
                    try:
                        handler_data.callback(signal, handler_data.data)
                    except ExitMainLoop:
                        raise
            if return_after is not None and isinstance(signal, return_after):
                return

    def _raise_exception(self, signal, data):
        raise signal.exception_info[0] from signal.exception_info[1]


class EventHandler(object):
    """Data class to save event handlers."""

    def __init__(self, callback, data):
        self.callback = callback
        self.data = data
