# Set of default signals used inside of widgets.
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

from sys import exc_info
from simpleline.event_loop import AbstractSignal

__all__ = ["ExceptionSignal", "InputReadySignal", "RenderScreenSignal", "CloseScreenSignal",
           "InputReceivedSignal"]


class ExceptionSignal(AbstractSignal):
    """Emit this signal when exception is raised.

    This class must be created inside of exception handler or `exception_info` must be specified
    in creation process.

    If you register handler for this exception then the Simpleline's exception handling
    is disabled!
    """

    def __init__(self, source, exception_info=None):
        """Create exception signal with higher priority (-20) than other signals.

        :param source: source of this signal
        :type source: class which emits this signal

        :param exception_info: if specified raise your exception, otherwise create exception here;
                               to create exception here it needs to be created inside of exception
                               handler
        :type exception_info: output of `sys.exc_info()` method
        """
        super().__init__(source, priority=-20)
        if exception_info:
            self.exception_info = exception_info
        else:
            self.exception_info = exc_info()


class InputReadySignal(AbstractSignal):
    """Input from user is ready for processing."""
    def __init__(self, source, input_handler_source, data, priority=0, success=True):
        """Store user input inside of this signal

        Read the data from user input in `data` attribute.

        The only way how a user should ask for input is to use InputHandler and inherited classes.
        The input_handler_source param must be set but this signal instance can be attached to
        another source object which is registered to a specific event loop.

        If no requester (object who uses InputHandler) is specified then source and
        input_handler_source will both point to InputHandler instance.

        :param source: Source of this signal.
        :type source: Any object.

        :param input_handler_source: InputHandler who is asking for input.
        :type input_handler_source: The `simpleline.input.input_handler.InputHandler` based
                                    instance.

        :param data: User input data.
        :type data: str

        :param priority: Priority of this event.
        :type priority: Int greater than 0.

        :param success: Was the input successful? True on successful input False otherwise.
        :type success: bool
        """
        super().__init__(source, priority=priority)
        self.input_handler_source = input_handler_source
        self.data = data
        self.success = success


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


class CloseScreenSignal(AbstractSignal):
    """Close current screen."""
