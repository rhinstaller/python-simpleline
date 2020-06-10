# Ticket machine synchronization class.
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
