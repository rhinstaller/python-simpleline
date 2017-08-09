# Widgets test classes.
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

from unittest import TestCase

from simpleline.event_loop.main_loop import TicketMachine


class TicketMachine_TestCase(TestCase):

    def setUp(self):
        self._tickets = TicketMachine()

    def test_take_ticket(self):
        line_id = 0
        t = self._tickets.take_ticket(line_id)
        self.assertEqual(t, 0)
        t2 = self._tickets.take_ticket(line_id)
        self.assertNotEqual(t, t2)

    def test_check_ticket(self):
        line_id = 0
        t = self._tickets.take_ticket(line_id)

        self.assertFalse(self._tickets.check_ticket(line_id, t))

        self._tickets.mark_line_to_go(line_id)

        self.assertTrue(self._tickets.check_ticket(line_id, t))

    def test_mark_multiple_tickets(self):
        line_id = 0

        t1 = self._tickets.take_ticket(line_id)
        t2 = self._tickets.take_ticket(line_id)
        t3 = self._tickets.take_ticket(line_id)
        t4 = self._tickets.take_ticket(line_id)

        self._tickets.mark_line_to_go(line_id)
        self.assertTrue(self._tickets.check_ticket(line_id, t1))
        self.assertTrue(self._tickets.check_ticket(line_id, t2))
        self.assertTrue(self._tickets.check_ticket(line_id, t3))
        self.assertTrue(self._tickets.check_ticket(line_id, t4))

    def test_mark_one_of_lines(self):
        line_id1 = "a"
        line_id2 = "b"

        t1 = self._tickets.take_ticket(line_id1)
        t2 = self._tickets.take_ticket(line_id1)
        t3 = self._tickets.take_ticket(line_id2)
        t4 = self._tickets.take_ticket(line_id2)

        self._tickets.mark_line_to_go(line_id1)

        self.assertTrue(self._tickets.check_ticket(line_id1, t1))
        self.assertTrue(self._tickets.check_ticket(line_id1, t2))
        self.assertFalse(self._tickets.check_ticket(line_id2, t3))
        self.assertFalse(self._tickets.check_ticket(line_id2, t4))

    def text_check_re_using(self):
        line_id = "a"

        t1 = self._tickets.take_ticket(line_id)
        t2 = self._tickets.take_ticket(line_id)
        t3 = self._tickets.take_ticket(line_id)

        self._tickets.mark_line_to_go(line_id)

        self.assertTrue(self._tickets.check_ticket(line_id, t1))
        self.assertTrue(self._tickets.check_ticket(line_id, t2))

        # it needs to be False when you check it again
        self.assertFalse(self._tickets.check_ticket(line_id, t1))
        self.assertFalse(self._tickets.check_ticket(line_id, t2))

        # take new ticket and mark the line again

        t4 = self._tickets.take_ticket(line_id)

        self._tickets.mark_line_to_go(line_id)

        # old checked tickets should be invalid now
        self.assertFalse(self._tickets.check_ticket(line_id, t1))
        self.assertFalse(self._tickets.check_ticket(line_id, t2))
        # old not checked ticket should work
        self.assertTrue(self._tickets.check_ticket(line_id, t3))
        # new tickets should work
        self.assertTrue(self._tickets.check_ticket(line_id, t4))
