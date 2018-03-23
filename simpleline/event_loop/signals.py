# Set of default signals used inside of widgets.
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

from sys import exc_info
from simpleline.event_loop import AbstractSignal

__all__ = ["ExceptionSignal", "InputReadySignal", "RenderScreenSignal", "CloseScreenSignal",
           "InputReceivedSignal"]


class ExceptionSignal(AbstractSignal):
    """Emit this signal when exception is raised.

    This class must be created inside of exception handler or `exception_info` must be specified in creation process.

    If you register handler for this exception then the Simpleline's exception handling is disabled!
    """

    def __init__(self, source, exception_info=None):
        """Create exception signal with higher priority (-20) than other signals.

        :param source: source of this signal
        :type source: class which emits this signal

        :param exception_info: if specified raise your exception, otherwise create exception here;
                               to create exception here it needs to be created inside of exception handler
        :type exception_info: output of `sys.exc_info()` method
        """
        super().__init__(source, priority=-20)
        if exception_info:
            self.exception_info = exception_info
        else:
            self.exception_info = exc_info()


class InputReadySignal(AbstractSignal):
    """Input from user is ready for processing."""
    def __init__(self, source, data, priority=0):
        """Store user input inside of this signal

        Read the data from user input in `data` attribute.

        :param source: Source of this signal.
        :type source: Any object.

        :param data: User input data.
        :type data: str

        :param priority: Priority of this event.
        :type priority: Int greater than 0.
        """
        super().__init__(source, priority=priority)
        self.data = data


class InputReceivedSignal(AbstractSignal):
    """Raw input received.

    This signal will be further processed and InputReadySignal should be enqueued soon.
    Most probably you are looking for InputReadySignal instead.
    """
    def __init__(self, source, data, priority=0):
        super().__init__(source, priority=priority)
        self.data = data


class RenderScreenSignal(AbstractSignal):
    """Render UIScreen to terminal."""
    pass


class CloseScreenSignal(AbstractSignal):
    """Close current screen."""
