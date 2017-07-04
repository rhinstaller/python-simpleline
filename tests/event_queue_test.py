# Event queue test classes.
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


import unittest
from unittest.mock import MagicMock
from simpleline.event_loop.event_queue import EventQueue, EventQueueError
from simpleline.event_loop.signals import AbstractSignal


class EventQueue_TestCase(unittest.TestCase):

    def setUp(self):
        self.e = EventQueue()

    def test_queue_is_empty(self):
        self.assertTrue(self.e.empty())

    def test_enqueue(self):
        fake_signal = MagicMock()

        self.e.enqueue(fake_signal)
        self.assertFalse(self.e.empty())

        self.assertEqual(fake_signal, self.e.get())
        self.assertTrue(self.e.empty())

    def test_enqueue_priority(self):
        signal_low_priority = TestSignal(priority=10)
        signal_high_priority = TestSignal(priority=0)

        self.e.enqueue(signal_low_priority)
        self.e.enqueue(signal_high_priority)

        self.assertEqual(signal_high_priority, self.e.get())
        self.assertEqual(signal_low_priority, self.e.get())

        # Test adding signals in different order (result shouldn't change)
        self.e.enqueue(signal_high_priority)
        self.e.enqueue(signal_low_priority)

        self.assertEqual(signal_high_priority, self.e.get())
        self.assertEqual(signal_low_priority, self.e.get())

    def test_adding_event_source(self):
        fake_source = MagicMock()
        self.e.add_source(fake_source)

        self.assertTrue(self.e.contains_source(fake_source))

    def test_removing_event_source(self):
        fake_source = MagicMock()
        self.e.add_source(fake_source)

        self.e.remove_source(fake_source)

        self.assertFalse(self.e.contains_source(fake_source))

    def test_remove_empty_source(self):
        with self.assertRaises(EventQueueError):
            self.e.remove_source(MagicMock())

    def test_enqueue_if_source_belongs(self):
        source = MagicMock()
        signal = TestSignal(source=source)

        self.e.add_source(source)
        self.assertTrue(self.e.enqueue_if_source_belongs(signal, source))
        self.assertEqual(signal, self.e.get())

    def test_enqueue_if_source_does_not_belong(self):
        signal = TestSignal()
        signal_low_priority = TestSignal(priority=25)

        # the get method will wait if nothing present so adding low priority signal below give us check if the queue
        # is really empty
        self.e.enqueue(signal_low_priority)

        self.assertFalse(self.e.enqueue_if_source_belongs(signal, MagicMock()))
        self.assertEqual(signal_low_priority, self.e.get())


class TestSignal(AbstractSignal):

    def __init__(self, source=None, priority=20):
        super().__init__(source, priority)
