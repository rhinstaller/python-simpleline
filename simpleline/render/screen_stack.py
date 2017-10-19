# Classes implementation for storing and manipulating Screen stack.
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


from simpleline.errors import SimplelineError


class ScreenStackException(SimplelineError):
    """General screen stack exception."""
    pass


class ScreenStackEmptyException(ScreenStackException):
    """Screen stack exception when stack is empty."""
    pass


class ScreenStack(object):
    """Managing screen stack used in `ScreenScheduler`."""

    def __init__(self):
        self._screens = []

    def empty(self):
        """Test if screen stack is empty.

        :return: True if empty.
        :rtype: bool
        """
        return not self._screens

    def size(self):
        """Get size of the stack.

        :return: Size of the stack.
        """
        return len(self._screens)

    def append(self, screen):
        """Add new screen to the top of the stack.

        :param screen: Screen for the future rendering.
        :type screen: Class based on `simpleline.render.ui_screen.UIScreen`.
        """
        self._screens.append(screen)

    def pop(self, remove=True):
        """Return top item from the stack.

        :param remove: If True (default) also remove this items from the stack.
        :return: The top screen on the stack.
        """
        try:
            if remove:
                return self._screens.pop()
            else:
                return self._screens[-1]
        except IndexError as e:
            raise ScreenStackEmptyException(e)

    def add_first(self, screen):
        """Add `screen` to the bottom of the stack.

        :param screen: Add the `screen` to the bottom of the stack.
        :type screen: Class based on `simpleline.render.ui_screen.UIScreen`.
        """
        self._screens.insert(0, screen)

    def dump_stack(self):
        """Dump screen stack structure.

        :returns: Screen stack representation.
        :rtype: str
        """
        msg = '======= Screen stack =======\n'
        msg += '----------- TOP ------------\n'

        for screen in reversed(self._screens):
            msg += str(screen)
            msg += "\n"

        msg += '============================\n'

        return msg


class ScreenData(object):
    """Inner data class to store screen data."""

    def __init__(self, ui_screen, args=None, execute_new_loop=False):
        self.ui_screen = ui_screen
        self.args = args
        self.execute_new_loop = execute_new_loop

    def __str__(self):
        msg = self.__class__.__name__
        msg += "("
        msg += ",".join((str(self.ui_screen), str(self.args), str(self.execute_new_loop)))
        msg += ")"
        return msg
