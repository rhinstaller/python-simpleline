# Rendering screen test classes.
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

from unittest.mock import Mock, patch
from threading import Barrier, current_thread, Event

from io import StringIO

from simpleline import App
from simpleline.event_loop.main_loop import MainLoop
from simpleline.input.input_handler import InputHandler, PasswordInputHandler
from simpleline.render.prompt import Prompt


@patch('sys.stdout', new_callable=StringIO)
@patch('simpleline.input.input_handler.InputHandlerRequest._get_input')
class InputHandler_TestCase(unittest.TestCase):

    def create_loop(self):
        self.loop = MainLoop()

    def setUp(self):
        super().setUp()
        self.create_loop()
        App.initialize(event_loop=self.loop)

        self._callback_called = False
        self._callback_input = ""

        self._callback_called2 = False
        self._callback_input2 = ""

        self._thread_barrier = Barrier(2, timeout=3)
        self._thread_event_wait_for_inner = Event()
        self._thread_event_wait_for_outer = Event()
        self._threads = []

    def tearDown(self):
        super().tearDown()
        self._thread_event_wait_for_outer.set()

        for t in self._threads:
            t.join()

        # process InputReceivedSignal
        App.get_event_loop().process_signals()
        # process InputReadySignal
        App.get_event_loop().process_signals()

    def test_async_input(self, input_mock, output_mock):
        input_mock.return_value = 'a'

        h = InputHandler()
        h.get_input(Prompt(message="ABC"))
        h.wait_on_input()

        self.assertEqual(h.value, 'a')

    def test_input_received(self, input_mock, output_mock):
        input_mock.return_value = 'a'

        h = InputHandler()

        self.assertFalse(h.input_received())

        h.get_input(Prompt(message="ABC"))
        h.wait_on_input()

        self.assertTrue(h.input_received())

    def test_input_callback(self, input_mock, output_mock):
        input_value = 'abc'
        input_mock.return_value = input_value

        h = InputHandler()
        h.set_callback(self._test_callback)
        h.get_input(Prompt(message="ABC"))
        h.wait_on_input()

        self.assertTrue(self._callback_called)
        self.assertEqual(self._callback_input, input_value)
        self.assertEqual(h.value, input_value)

    def test_concurrent_input(self, input_mock, output_mock):
        input_mock.side_effect = self._wait_for_concurrent_call

        h = InputHandler()
        h.set_callback(self._test_callback)
        h2 = InputHandler()
        h2.set_callback(self._test_callback2)

        with self.assertRaisesRegex(KeyError, r'.*Input handler:.*InputHandler object'
                                              r'.*Input requester: Unknown'
                                              r'.*Input handler:.*InputHandler object'
                                              r'.*Input requester: Unknown.*'):
            h.get_input(Prompt(message="ABC"))
            self._thread_event_wait_for_inner.wait()
            h2.get_input(Prompt(message="ABC"))

        self.assertFalse(self._callback_called)
        self.assertEqual(self._callback_input, "")
        self.assertEqual(h.value, None)

        self.assertFalse(self._callback_called2)
        self.assertEqual(self._callback_input2, "")
        self.assertEqual(h2.value, None)

    def test_concurrent_input_with_source(self, input_mock, output_mock):
        input_mock.side_effect = self._wait_for_concurrent_call
        source1 = Mock()
        source2 = Mock()

        h = InputHandler(source=source1)
        h2 = InputHandler(source=source2)
        h.set_callback(self._test_callback)
        h2.set_callback(self._test_callback2)

        with self.assertRaisesRegex(KeyError, r'.*Input handler:.*InputHandler object'
                                              r'.*Input requester:.*Mock'
                                              r'.*Input handler:.*InputHandler object'
                                              r'.*Input requester:.*Mock.*'):
            h.get_input(Prompt(message="ABC"))
            self._thread_event_wait_for_inner.wait()
            h2.get_input(Prompt(message="ABC"))

        self.assertFalse(self._callback_called)
        self.assertEqual(self._callback_input, "")
        self.assertEqual(h.value, None)

        self.assertFalse(self._callback_called2)
        self.assertEqual(self._callback_input2, "")
        self.assertEqual(h2.value, None)

    def test_concurrent_input_without_check(self, input_mock, output_mock):
        input_mock.side_effect = self._wait_for_concurrent_call

        h = InputHandler()
        h2 = InputHandler()
        h.set_callback(self._test_callback)
        h2.set_callback(self._test_callback2)
        h2.skip_concurrency_check = True
        h.skip_concurrency_check = True

        h.get_input(Prompt(message="ABC"))
        self._thread_event_wait_for_inner.wait()
        h2.get_input(Prompt(message="ABC"))
        self._thread_event_wait_for_outer.set()

        h.wait_on_input()
        h2.wait_on_input()

        self.assertFalse(self._callback_called)
        self.assertFalse(h.input_successful())

        self.assertTrue(self._callback_called2)
        self.assertTrue(h2.input_successful())
        self.assertEqual(self._callback_input2, "thread 0")
        self.assertEqual(h2.value, "thread 0")

    def _wait_for_concurrent_call(self):
        ret = "thread {}".format(len(self._threads))
        self._threads.append(current_thread())
        self._thread_event_wait_for_inner.set()
        self._thread_event_wait_for_outer.wait()
        return ret

    def _test_callback(self, user_input):
        self._callback_called = True
        self._callback_input = user_input

    def _test_callback2(self, user_input):
        self._callback_called2 = True
        self._callback_input2 = user_input


@patch('sys.stdout', new_callable=StringIO)
@patch('simpleline.global_configuration.GlobalConfiguration.password_function')
class PasswordInputHandler_TestCase(unittest.TestCase):

    def create_loop(self):
        self.loop = MainLoop()

    def setUp(self):
        super().setUp()
        self.create_loop()
        App.initialize(event_loop=self.loop)

        self._callback_called = False
        self._callback_input = ""

    def test_async_input(self, input_mock, output_mock):
        input_mock.return_value = 'a'

        h = PasswordInputHandler()
        h.get_input(Prompt(message="ABC"))
        h.wait_on_input()

        self.assertEqual(h.value, 'a')

    def test_input_received(self, input_mock, output_mock):
        input_mock.return_value = 'a'

        h = PasswordInputHandler()

        self.assertFalse(h.input_received())

        h.get_input(Prompt(message="ABC"))
        h.wait_on_input()

        self.assertTrue(h.input_received())

    def test_input_callback(self, input_mock, output_mock):
        input_value = 'abc'
        input_mock.return_value = input_value

        h = PasswordInputHandler()
        h.set_callback(self._test_callback)
        h.get_input(Prompt(message="ABC"))
        h.wait_on_input()

        self.assertTrue(self._callback_called)
        self.assertEqual(self._callback_input, input_value)
        self.assertEqual(h.value, input_value)

    def _test_callback(self, user_input):
        self._callback_called = True
        self._callback_input = user_input
