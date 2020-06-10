# Global configuration for the whole application.
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

from getpass import getpass

__all__ = ["GlobalConfiguration"]

DEFAULT_WIDTH = 80
DEFAULT_PASSWORD_FUNC = getpass


class GlobalConfiguration(object):
    """Class for global configuration of application defaults.

    All stored data are persistent between App.initialize() calls and can be used before this call.
    """

    def __init__(self):
        self._width = DEFAULT_WIDTH
        self._getpass = DEFAULT_PASSWORD_FUNC
        self._run_with_empty_stack = False

    @property
    def width(self):
        """Get width of the application.

        :returns: int
        """
        return self._width

    @width.setter
    def width(self, width):
        """Set width of the application.

        :param width: Number of characters which can be printed to one line.
        :type width: int
        """
        self._width = width

    def clear_width(self):
        """Clear user defined width and set the default.

         Default: 80 characters
         """
        self._width = DEFAULT_WIDTH

    @property
    def password_function(self):
        """Get function to get user passwords from a console.

        :returns: Function with one argument which is text representation of prompt.
        """
        return self._getpass

    @password_function.setter
    def password_function(self, password_func):
        """Set function to get user passwords from a console.

        :param password_func: Function to get password from a command line.
        :type password_func: Function with one argument which is text representation of prompt.
        """
        self._getpass = password_func

    def clear_password_function(self):
        """Clear user defined password function and set the default.

        Default: getpass.getpass function
        """
        self._getpass = getpass

    @property
    def should_run_with_empty_stack(self):
        """Should test on empty screen stack when starting event loop.

        :returns: If False the App.run() call will end with an exception (default), True otherwise.
        """
        return self._run_with_empty_stack

    @should_run_with_empty_stack.setter
    def should_run_with_empty_stack(self, value):
        """Set if the App.run() call should end with an exception when screen stack is empty.

        This can be valuable when you want to schedule a screen later by an other thread.

        :param value: If False the App.run() call will end with an exception, if True it will
                        run with nothing displayed.
        """
        self._run_with_empty_stack = value

    def clear_should_run_with_empty_stack(self):
        """Clear user defined test to run with an empty screen stack.

        Default: False
        """
        self._run_with_empty_stack = False
