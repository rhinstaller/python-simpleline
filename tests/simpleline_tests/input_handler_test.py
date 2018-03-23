# Rendering screen test classes.
#
# Copyright (C) 2018  Red Hat, Inc.
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
from unittest import mock
from io import StringIO

from simpleline import App
from simpleline.event_loop.main_loop import MainLoop
from simpleline.input.input_handler import InputHandler, PasswordInputHandler
from simpleline.render.prompt import Prompt


@mock.patch('sys.stdout', new_callable=StringIO)
@mock.patch('simpleline.input.input_handler.InputHandlerRequest._get_input')
class InputHandler_TestCase(unittest.TestCase):

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

    def _test_callback(self, user_input):
        self._callback_called = True
        self._callback_input = user_input


@mock.patch('sys.stdout', new_callable=StringIO)
@mock.patch('getpass.getpass')
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
