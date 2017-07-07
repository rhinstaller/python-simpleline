# Signal handler is giving ability connect and emit to all widgets.
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

from simpleline.base import App
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
        :type signal: class based on `simpleline.event_loop.AbstractSignal

        :param callback: the callback function
        :type callback: func(event_message, data)

        :param data: Data you want to pass to the callback
        :type data: Anything
        """
        App.event_loop().register_signal_handler(signal, callback, data)

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
        App.event_loop().enqueue_signal(signal)

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
        App.event_loop().enqueue_signal(signal)

    def close(self):
        """Emit signal to close this screen.

        Add CloseScreenSignal to the event loop.
        """
        signal = self.create_signal(CloseScreenSignal)
        App.event_loop().enqueue_signal(signal)
