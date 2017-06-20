import unittest
from unittest.mock import patch, MagicMock

from simpleline.render.ui_screen import UIScreen
from simpleline.event_loop.signals import RenderScreenSignal, AbstractSignal

from simpleline.base import App


class SignalHandler_TestCase(unittest.TestCase):

    def setUp(self):
        self.callback_called = False
        self.priority = 0

    def _callback(self, signal, data):
        self.callback_called = True
        signal.test_attribute = True

    def test_basic_connect(self):
        connect_screen = UIScreen()

        App.initialize("TestApp", renderer=MagicMock())
        connect_screen.connect(TestSignal, self._callback)
        App.event_loop().enqueue_signal(TestSignal(self))
        App.event_loop().process_signals()

        self.assertTrue(self.callback_called)

    def test_create_signal(self):
        connect_screen = UIScreen()

        App.initialize("TestApp", renderer=MagicMock())
        signal = connect_screen.create_signal(TestSignal, priority=20)

        self.assertEqual(signal.priority, 20)
        self.assertTrue(isinstance(signal, TestSignal))
        # source is set by create_signal
        self.assertEqual(signal.source, connect_screen)

    def test_emit(self):
        connect_screen = UIScreen()

        App.initialize("TestApp", renderer=MagicMock())
        connect_screen.connect(TestSignal, self._callback)
        connect_screen.emit(TestSignal(self))
        App.event_loop().process_signals()

        self.assertTrue(self.callback_called)

    @patch('sys.stdout')
    def test_connect_react_on_rendering(self, _):
        connect_test_screen = TestRenderConnectHandler()
        screen2 = EmptyScreen()

        App.initialize("Test")
        App.renderer().schedule_screen(connect_test_screen)
        App.renderer().schedule_screen(screen2)
        App.run()

        self.assertTrue(connect_test_screen.callback_called)


class TestRenderConnectHandler(UIScreen):

    def __init__(self):
        super().__init__()
        self.callback_called = False

    def refresh(self, args=None):
        super().refresh(args)
        self.connect(RenderScreenSignal, self._callback)
        self.close()
        return False

    def _callback(self, signal, args):
        self.callback_called = True


class EmptyScreen(UIScreen):

    def refresh(self, args=None):
        super().refresh(args=args)
        return False

    def show_all(self):
        super().show_all()
        self.close()


class TestSignal(AbstractSignal):
    pass
