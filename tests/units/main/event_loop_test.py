# Event loop test classes.
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

import unittest

from simpleline.event_loop import AbstractSignal
from simpleline.event_loop import EventHandler
from simpleline.event_loop import ExitMainLoop
from simpleline.event_loop.main_loop import MainLoop


class EventLoopHandler_TestCase(unittest.TestCase):

    def callback_func(self):
        pass

    def test_signal_handler_named_params(self):
        data = [1, 2, "args"]
        ev = EventHandler(callback=self.callback_func, data=data)

        self.assertEqual(ev.callback, self.callback_func)
        self.assertEqual(ev.data, data)

    def test_signal_handler_positional_params(self):
        data = [1, 3, "args"]
        ev = EventHandler(self.callback_func, data)

        self.assertEqual(ev.callback, self.callback_func)
        self.assertEqual(ev.data, data)


class ProcessEvents_TestCase(unittest.TestCase):

    def setUp(self):
        self.signal_counter = 0
        self.signal_counter2 = 0
        self.signal_counter_copied = 0
        self.callback_called = False
        self.callback_args = None
        self.create_loop()

    def create_loop(self):
        self.loop = MainLoop()

    def test_simple_register_handler(self):
        self.callback_called = False

        loop = self.loop
        loop.register_signal_handler(SignalMock, self._handler_callback)
        loop.enqueue_signal(SignalMock())
        loop.process_signals()

        self.assertTrue(self.callback_called)

    def test_process_more_signals(self):
        self.signal_counter = 0

        loop = self.loop
        loop.register_signal_handler(SignalMock, self._handler_signal_counter)
        loop.enqueue_signal(SignalMock())
        loop.enqueue_signal(SignalMock())
        loop.enqueue_signal(SignalMock())
        loop.process_signals()

        self.assertEqual(self.signal_counter, 3)

    def test_process_signals_multiple_times(self):
        self.signal_counter = 0

        loop = self.loop
        loop.register_signal_handler(SignalMock, self._handler_signal_counter)
        loop.enqueue_signal(SignalMock())
        loop.enqueue_signal(SignalMock())
        loop.process_signals()
        self.assertEqual(self.signal_counter, 2)

        loop.enqueue_signal(SignalMock())
        loop.enqueue_signal(SignalMock())
        loop.process_signals()
        self.assertEqual(self.signal_counter, 4)

    def test_wait_on_signal(self):
        self.signal_counter = 0

        loop = self.loop
        loop.register_signal_handler(SignalMock,
                                     self._handler_signal_counter)
        loop.register_signal_handler(SignalMock2,
                                     self._handler_process_events_then_register_testsignal,
                                     loop)
        loop.enqueue_signal(SignalMock())
        loop.enqueue_signal(SignalMock2())
        loop.process_signals(return_after=SignalMock2)
        self.assertEqual(self.signal_counter, 1)

        loop.process_signals()
        self.assertEqual(self.signal_counter, 2)

    def test_wait_on_signal_skipped_by_inner_process_events(self):
        self.signal_counter = 0

        loop = self.loop
        loop.register_signal_handler(SignalMock,
                                     self._handler_signal_counter)
        # run process signals recursively in this handler which will skip processing
        loop.register_signal_handler(SignalMock2,
                                     self._handler_process_events_then_register_testsignal,
                                     loop)
        loop.enqueue_signal(SignalMock2())
        loop.enqueue_signal(SignalMock())
        # new signal will be registered in handler method but that shouldn't be processed
        # because it should end on the first signal even when it was skipped
        loop.process_signals(return_after=SignalMock)

        self.assertEqual(self.signal_counter, 1)

    def test_multiple_handlers_to_signal(self):
        self.signal_counter = 0
        self.signal_counter2 = 0

        loop = self.loop
        loop.register_signal_handler(SignalMock, self._handler_signal_counter)
        loop.register_signal_handler(SignalMock, self._handler_signal_counter2)
        loop.enqueue_signal(SignalMock())
        loop.enqueue_signal(SignalMock())
        loop.process_signals()

        self.assertEqual(self.signal_counter, 2)
        self.assertEqual(self.signal_counter2, 2)

    def test_priority_signal_processing(self):
        self.signal_counter = 0

        loop = self.loop
        loop.register_signal_handler(SignalMock, self._handler_signal_counter)
        loop.register_signal_handler(PrioritySignalMock, self._handler_signal_counter)
        loop.enqueue_signal(SignalMock())
        loop.enqueue_signal(SignalMock())
        # should be processed as first signal because of priority
        loop.enqueue_signal(PrioritySignalMock())
        loop.enqueue_signal(SignalMock())
        loop.process_signals()
        self.assertEqual(self.signal_counter, 1)

        # process rest of the signals
        loop.process_signals()
        self.assertEqual(self.signal_counter, 4)

    def test_low_priority_signal_processing(self):
        self.signal_counter = 0
        self.signal_counter_copied = 0

        loop = self.loop
        loop.register_signal_handler(SignalMock, self._handler_signal_counter)
        loop.register_signal_handler(LowPrioritySignalMock, self._handler_signal_copy_counter)
        loop.enqueue_signal(SignalMock())
        loop.enqueue_signal(LowPrioritySignalMock())
        loop.enqueue_signal(SignalMock())
        loop.enqueue_signal(SignalMock())
        loop.process_signals()
        self.assertEqual(self.signal_counter, 3)

        # process the low priority signal
        loop.process_signals()
        self.assertEqual(self.signal_counter_copied, 3)

    def test_quit_callback(self):
        self.callback_called = False
        self.callback_args = None
        msg = "Test data"

        loop = self.loop
        loop.set_quit_callback(self._handler_quit_callback, args=msg)
        loop.register_signal_handler(SignalMock, self._handler_raise_ExitMainLoop_exception)
        loop.enqueue_signal(SignalMock())
        loop.run()

        self.assertTrue(self.callback_called)
        self.assertEqual(msg, self.callback_args)

    def test_force_quit(self):
        self.callback_called = False

        loop = self.loop
        loop.register_signal_handler(SignalMock, self._handler_callback)
        loop.register_signal_handler(SignalMock2, self._handler_force_quit_exception)
        loop.enqueue_signal(SignalMock2())
        loop.enqueue_signal(SignalMock())
        loop.run()

        self.assertFalse(self.callback_called)

    def test_force_quit_recursive_loop(self):
        self.callback_called = False

        loop = self.loop
        loop.register_signal_handler(SignalMock,
                                     self._handler_start_inner_loop_and_enqueue_event,
                                     SignalMock3())
        loop.register_signal_handler(SignalMock2,
                                     self._handler_callback)
        loop.register_signal_handler(SignalMock3,
                                     self._handler_force_quit_exception)
        loop.enqueue_signal(SignalMock())
        loop.enqueue_signal(SignalMock2())
        loop.run()

        self.assertFalse(self.callback_called)

    def test_force_quit_when_waiting_on_signal(self):
        self.callback_called = False

        loop = self.loop
        loop.register_signal_handler(SignalMock, self._handler_force_quit_exception)
        loop.register_signal_handler(SignalMock2, self._handler_callback)
        loop.enqueue_signal(SignalMock())
        loop.enqueue_signal(SignalMock2())

        # FIXME: Find a better way how to detect infinite loop
        # if force quit won't work properly this will hang up
        loop.process_signals(return_after=SignalMock3)

        self.assertFalse(self.callback_called)

    # HANDLERS FOR TESTING
    def _handler_callback(self, signal, data):
        self.callback_called = True

    def _handler_quit_callback(self, args):
        self.callback_called = True
        self.callback_args = args

    def _handler_signal_counter(self, signal, data):
        self.signal_counter += 1

    def _handler_signal_counter2(self, signal, data):
        self.signal_counter2 += 1

    def _handler_signal_copy_counter(self, signal, data):
        self.signal_counter_copied = self.signal_counter

    @staticmethod
    def _handler_process_events_then_register_testsignal(signal, data):
        event_loop = data
        event_loop.process_signals()
        # This shouldn't be processed
        event_loop.enqueue_signal(SignalMock())

    def _handler_start_inner_loop_and_enqueue_event(self, signal, data):
        self.loop.execute_new_loop(data)

    @staticmethod
    def _handler_raise_ExitMainLoop_exception(signal, data):
        raise ExitMainLoop()

    def _handler_force_quit_exception(self, signal, data):
        self.loop.force_quit()


# TESTING EVENTS
class SignalMock(AbstractSignal):

    def __init__(self):
        # ignore source
        super().__init__(None)


class SignalMock2(AbstractSignal):

    def __init__(self):
        # ignore source
        super().__init__(None)


class SignalMock3(AbstractSignal):

    def __init__(self):
        # ignore source
        super().__init__(None)


class PrioritySignalMock(AbstractSignal):

    def __init__(self):
        # ignore source
        super().__init__(None, -10)


class LowPrioritySignalMock(AbstractSignal):

    def __init__(self):
        # ignore source
        super().__init__(None, 20)
