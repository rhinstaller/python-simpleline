# Global configuration for the whole application.
#
# Copyright (C) 2018  Red Hat, Inc.
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

        This function takes one parameter which is text representation of a prompt.

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
