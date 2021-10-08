# Screen stack test classes.
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


import unittest

from simpleline.render.screen import UIScreen
from simpleline.render.screen_stack import ScreenStack, ScreenData, ScreenStackEmptyException


class ScreenStack_TestCase(unittest.TestCase):

    def test_append_screen(self):
        stack = ScreenStack()
        stack.append(ScreenData(None))

    def test_is_empty(self):
        stack = ScreenStack()
        self.assertTrue(stack.empty())
        stack.append(ScreenData(None))
        self.assertFalse(stack.empty())

    def test_pop(self):
        stack = ScreenStack()
        with self.assertRaises(ScreenStackEmptyException):
            stack.pop()

        with self.assertRaises(ScreenStackEmptyException):
            stack.pop(False)

        # stack.pop(True) will remove the item
        stack.append(ScreenData(None))
        stack.pop(True)
        with self.assertRaises(ScreenStackEmptyException):
            stack.pop()

        # stack.pop() should behave the same as stack.pop(True)
        stack.append(ScreenData(None))
        stack.pop()
        with self.assertRaises(ScreenStackEmptyException):
            stack.pop()

        stack.append(ScreenData(None))
        stack.pop(False)
        stack.pop(True)

    def test_add_first(self):
        stack = ScreenStack()

        screen_data = ScreenData(None)
        stack.add_first(screen_data)
        self.assertEqual(stack.pop(False), screen_data)

        # Add new Screen data to the end
        new_screen_data = ScreenData(None)
        stack.add_first(new_screen_data)
        # First the old screen data should be there
        self.assertEqual(stack.pop(), screen_data)
        # Second should be the new screen data
        self.assertEqual(stack.pop(), new_screen_data)

    def test_size(self):
        stack = ScreenStack()
        self.assertEqual(stack.size(), 0)

        stack.append(ScreenData(None))
        self.assertEqual(stack.size(), 1)

        stack.append(ScreenData(None))
        self.assertEqual(stack.size(), 2)

        # Remove from stack
        stack.pop()
        self.assertEqual(stack.size(), 1)
        stack.pop()
        self.assertEqual(stack.size(), 0)

        # Add first when stack has items
        stack.append(ScreenData(None))
        stack.append(ScreenData(None))
        self.assertEqual(stack.size(), 2)
        stack.add_first(ScreenData(None))
        self.assertEqual(stack.size(), 3)

    def test_stack_dump(self):
        stack = ScreenStack()

        stack.append(ScreenData(ScreenMock1()))
        stack.append(ScreenData(ScreenMock2()))

        dump = stack.dump_stack()
        dump = dump.replace('\n', '')
        self.assertRegex(dump, r"ScreenMock2.*ScreenMock1")


class ScreenData_TestCase(unittest.TestCase):

    def setUp(self):
        self.ui_screen = None

    def _prepare(self):
        self.ui_screen = UIScreen()

    def _screen_check(self, test_screen, ui_screen, args, execute_new_loop):
        self._prepare()
        self.assertEqual(test_screen.ui_screen, ui_screen)
        self.assertEqual(test_screen.args, args)
        self.assertEqual(test_screen.execute_new_loop, execute_new_loop)

    def test_screen_data(self):
        self._prepare()
        screen = ScreenData(self.ui_screen)
        self._screen_check(screen, self.ui_screen, None, False)

    def test_screen_data_with_args(self):
        self._prepare()
        screen = ScreenData(ui_screen=self.ui_screen, args=1)
        self._screen_check(screen, self.ui_screen, 1, False)

        array = [2, "a"]
        screen2 = ScreenData(ui_screen=self.ui_screen, args=array)
        self._screen_check(screen2, self.ui_screen, array, False)

    def test_screen_data_with_execute_loop(self):
        self._prepare()
        screen = ScreenData(self.ui_screen, execute_new_loop=True)
        self._screen_check(screen, self.ui_screen, None, True)

        screen2 = ScreenData(self.ui_screen, execute_new_loop=False)
        self._screen_check(screen2, self.ui_screen, None, False)

    def test_screen_data_with_args_and_execute_loop(self):
        self._prepare()
        screen = ScreenData(self.ui_screen, "test", True)
        self._screen_check(screen, self.ui_screen, "test", True)


class ScreenMock1(UIScreen):
    pass


class ScreenMock2(UIScreen):
    pass
