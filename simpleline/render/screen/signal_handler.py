# Signal handler is giving ability connect and emit to all widgets.
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

from simpleline import App
from simpleline.event_loop.signals import RenderScreenSignal, CloseScreenSignal


class SignalHandler(object):
    """Provides methods for handling signals anc callbacks.

    Provides main methods:
        `connect()`       -- connect this widget on given signal
        `create_signal()` -- create signal class which can be used in the emit method
        `emit()`          -- emit signal given signal
    """

    def connect(self, signal, callback, data=None):
        """Connect this class method with given signal.

        :param signal: signal class which you want to connect
        :type signal: class based on `simpleline.event_loop.AbstractSignal`

        :param callback: the callback function
        :type callback: func(event_message, data)

        :param data: Data you want to pass to the callback
        :type data: Anything
        """
        App.get_event_loop().register_signal_handler(signal, callback, data)

    def create_signal(self, signal_class, priority=0):
        """Create signal instance usable in the emit method.

        :param signal_class: signal you want to use
        :type signal_class: class based on `simpleline.event_loop.AbstractSignal`

        :param priority: priority of the signal; please look on the `simpleline.event_loop.AbstractSignal.priority` for
                         further info
        :type priority: int
        """
        return signal_class(self, priority)

    def emit(self, signal):
        """Emit the signal.

        This will add `signal` to the event loop.

        :param signal: signal to emit
        :type signal: instance of class based on `simpleline.event_loop.AbstractSignal`
        """
        App.get_event_loop().enqueue_signal(signal)

    def create_and_emit(self, signal):
        """Create the signal and emit it.

        This is basically shortcut for calling `self.create_signal` and `self.emit`.
        """
        created_signal = self.create_signal(signal)
        self.emit(created_signal)

    def redraw(self):
        """Emit signal to initiate draw.

        Add RenderScreenSignal to the event loop.
        """
        signal = self.create_signal(RenderScreenSignal)
        App.get_event_loop().enqueue_signal(signal)

    def close(self):
        """Emit signal to close this screen.

        Add CloseScreenSignal to the event loop.
        """
        signal = self.create_signal(CloseScreenSignal)
        App.get_event_loop().enqueue_signal(signal)
