import unittest
from simpleline.event_loop.main_loop import EventHandler
from simpleline.event_loop.main_loop import MainLoop
from simpleline.event_loop import AbstractSignal


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

    def test_simple_register_handler(self):
        self.callback_called = False
        loop = MainLoop()
        loop.register_signal_handler(TestSignal, self._handler_callback)
        loop.enqueue_signal(TestSignal())
        loop.process_signals()
        self.assertTrue(self.callback_called)

    def test_process_more_signals(self):
        self.signal_counter = 0
        loop = MainLoop()
        loop.register_signal_handler(TestSignal, self._handler_signal_counter)
        loop.enqueue_signal(TestSignal())
        loop.enqueue_signal(TestSignal())
        loop.enqueue_signal(TestSignal())
        loop.process_signals()
        self.assertEqual(self.signal_counter, 3)

    def test_process_signals_multiple_times(self):
        self.signal_counter = 0
        loop = MainLoop()
        loop.register_signal_handler(TestSignal, self._handler_signal_counter)
        loop.enqueue_signal(TestSignal())
        loop.enqueue_signal(TestSignal())
        loop.process_signals()
        self.assertEqual(self.signal_counter, 2)
        loop.enqueue_signal(TestSignal())
        loop.enqueue_signal(TestSignal())
        loop.process_signals()
        self.assertEqual(self.signal_counter, 4)

    def test_return_after_more_signals_register_handler(self):
        self.signal_counter = 0
        loop = MainLoop()
        loop.register_signal_handler(TestSignal, self._handler_signal_counter)
        loop.enqueue_signal(TestSignal())
        loop.enqueue_signal(TestSignal2())
        loop.enqueue_signal(TestSignal())
        loop.process_signals(return_after=TestSignal2)
        self.assertEqual(self.signal_counter, 1)
        loop.process_signals()
        self.assertEqual(self.signal_counter, 2)

    def test_multiple_handlers_to_signal(self):
        self.signal_counter = 0
        self.signal_counter2 = 0
        loop = MainLoop()
        loop.register_signal_handler(TestSignal, self._handler_signal_counter)
        loop.register_signal_handler(TestSignal, self._handler_signal_counter2)
        loop.enqueue_signal(TestSignal())
        loop.enqueue_signal(TestSignal())
        loop.process_signals()
        self.assertEqual(self.signal_counter, 2)
        self.assertEqual(self.signal_counter2, 2)

    def test_priority_signal_processing(self):
        self.signal_counter = 0
        self.signal_counter_copied = 0
        loop = MainLoop()
        loop.register_signal_handler(TestSignal, self._handler_signal_counter)
        loop.register_signal_handler(TestPrioritySignal, self._handler_signal_copy_counter)
        loop.enqueue_signal(TestSignal())
        loop.enqueue_signal(TestSignal())
        loop.enqueue_signal(TestPrioritySignal())  # should be processed as first signal because of priority
        loop.enqueue_signal(TestSignal())
        loop.process_signals()
        self.assertEqual(self.signal_counter, 3)
        self.assertEqual(self.signal_counter_copied, 0)

    def test_low_priority_signal_processing(self):
        self.signal_counter = 0
        self.signal_counter_copied = 0
        loop = MainLoop()
        loop.register_signal_handler(TestSignal, self._handler_signal_counter)
        loop.register_signal_handler(TestLowPrioritySignal, self._handler_signal_copy_counter)
        loop.enqueue_signal(TestSignal())
        loop.enqueue_signal(TestLowPrioritySignal())
        loop.enqueue_signal(TestSignal())
        loop.enqueue_signal(TestSignal())
        loop.process_signals()
        self.assertEqual(self.signal_counter, 3)
        self.assertEqual(self.signal_counter_copied, 3)

    # HANDLERS FOR TESTING
    def _handler_callback(self, signal, data):
        self.callback_called = True

    def _handler_signal_counter(self, signal, data):
        self.signal_counter += 1

    def _handler_signal_counter2(self, signal, data):
        self.signal_counter2 += 1

    def _handler_signal_copy_counter(self, signal, data):
        self.signal_counter_copied = self.signal_counter


# TESTING EVENTS
class TestSignal(AbstractSignal):

    def __init__(self):
        # ignore source
        super().__init__(None)


class TestSignal2(AbstractSignal):

    def __init__(self):
        # ignore source
        super().__init__(None)


class TestPrioritySignal(AbstractSignal):

    def __init__(self):
        # ignore source
        super().__init__(None, -10)


class TestLowPrioritySignal(AbstractSignal):

    def __init__(self):
        # ignore source
        super().__init__(None, 20)
