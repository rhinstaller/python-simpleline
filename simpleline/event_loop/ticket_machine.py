# Ticket machine synchronization class.
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


class TicketMachine(object):
    """Hold signals processed by the event loop if someone wait on them.

    This is useful when recursive process events will skip required signal.
    """

    def __init__(self):
        self._lines = {}
        self._counter = 0

    def take_ticket(self, line_id):
        """Take ticket (id) and go line (processing events).

        Use `check_ticket` if you are ready to go.

        :param line_id: Line where you are waiting.
        :type line_id: Anything.
        """
        obj_id = self._counter
        if line_id not in self._lines:
            self._lines[line_id] = {obj_id: False}
        else:
            self._lines[line_id][obj_id] = False

        self._counter += 1
        return obj_id

    def check_ticket(self, line, unique_id):
        """Check if you are ready to go.

        If True the unique_id is not valid anymore.

        :param unique_id: Your id used to identify you in the line.
        :type unique_id: int

        :param line: Line where you are waiting.
        :type line: Anything.
        """
        if self._lines[line][unique_id]:
            return self._lines[line].pop(unique_id)

    def mark_line_to_go(self, line):
        """All in the `line` are ready to go.

        Mark all tickets in the line as True.

        :param line: Line which should processed.
        :type line: Anything.
        """
        if line in self._lines:
            our_line = self._lines[line]
            for key in our_line:
                our_line[key] = True
