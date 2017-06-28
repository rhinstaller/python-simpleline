# Signal handler test classes.
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

        App.initialize(renderer=MagicMock())
        connect_screen.connect(TestSignal, self._callback)
        App.event_loop().enqueue_signal(TestSignal(self))
        App.event_loop().process_signals()

        self.assertTrue(self.callback_called)

    def test_create_signal(self):
        connect_screen = UIScreen()

        App.initialize(renderer=MagicMock())
        signal = connect_screen.create_signal(TestSignal, priority=20)

        self.assertEqual(signal.priority, 20)
        self.assertTrue(isinstance(signal, TestSignal))
        # source is set by create_signal
        self.assertEqual(signal.source, connect_screen)

    def test_emit(self):
        connect_screen = UIScreen()

        App.initialize(renderer=MagicMock())
        connect_screen.connect(TestSignal, self._callback)
        connect_screen.emit(TestSignal(self))
        App.event_loop().process_signals()

        self.assertTrue(self.callback_called)

    @patch('sys.stdout')
    def test_connect_react_on_rendering(self, _):
        connect_test_screen = TestRenderConnectHandler()
        screen2 = EmptyScreen()

        App.initialize()
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
