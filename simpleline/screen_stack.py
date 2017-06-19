# Screen stack classes for manipulating stack which are in a view stack.
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


class ScreenStackException(Exception):
    pass


class ScreenStackEmptyException(ScreenStackException):
    pass


class ScreenStack(object):

    def __init__(self):
        self._screens = []

    def is_empty(self):
        if not self._screens:
            return True
        else:
            return False

    def size(self):
        return len(self._screens)

    def append(self, screen_item):
        self._screens.append(screen_item)

    def pop(self, remove=True):
        try:
            if remove:
                return self._screens.pop()
            else:
                return self._screens[-1]
        except IndexError as e:
            raise ScreenStackEmptyException(e)

    def add_first(self, screen):
        self._screens.insert(0, screen)


class ScreenData(object):

    def __init__(self, ui_screen, args=None, draw_immediately=False):
        self.ui_screen = ui_screen
        if args is None:
            self.args = []
        else:
            self.args = args
        self.draw_immediately = draw_immediately

    def __str__(self):
        msg = self.__class__.__name__
        msg += "("
        msg += ",".join((str(self.ui_screen), str(self.args), str(self.draw_immediately)))
        msg += ")"
        return msg
