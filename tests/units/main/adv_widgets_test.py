# Advanced widgets test cases.
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

from unittest.mock import patch
from io import StringIO

from simpleline.render.screen import UIScreen
from simpleline.input.input_handler import InputHandler
from simpleline.render.adv_widgets import GetInputScreen, GetPasswordInputScreen

from .. import UtilityMixin


class InputHandlerMock(InputHandler):
    """Dummy InputHandler instance.

    This class based on InputHandler has all threading logic disabled for simpler testing.
    """
    def _register_input_ready_signal(self):
        pass

    def get_input(self, prompt):
        pass

    def wait_on_input(self):
        pass


class UIScreen_TestCase(unittest.TestCase):
    @patch('simpleline.render.screen.input_manager.InputHandler')
    def test_uiscreen_disable_concurrency_check(self, input_handler_class_mock):
        # Replace default InputHandler instance created by InputManager by our mock to have
        # it stored after use.
        input_handler_instance_mock = InputHandlerMock()
        input_handler_class_mock.return_value = input_handler_instance_mock

        screen = UIScreen()
        input_manager = screen.input_manager
        input_manager.skip_concurrency_check = True
        screen.get_user_input("test")

        self.assertTrue(screen.input_manager.skip_concurrency_check)
        # Check that the created InputHandler instance has the flag correctly set.
        # We don't need to check the concurrency check functionality, it is tested
        # elsewhere already.
        self.assertTrue(input_handler_instance_mock.skip_concurrency_check)

    @patch('simpleline.render.screen.input_manager.InputHandler')
    def test_uiscreen_password_disable_concurrency_check(self, input_handler_class_mock):
        # Replace default InputHandler instance created by InputManager by our mock to have
        # it stored after use.
        input_handler_instance_mock = InputHandlerMock()
        input_handler_class_mock.return_value = input_handler_instance_mock

        screen = GetPasswordInputScreen(message="Test prompt")
        input_manager = screen.input_manager
        input_manager.skip_concurrency_check = True
        screen.get_user_input("test")

        self.assertTrue(screen.input_manager.skip_concurrency_check)
        # Check that the created InputHandler instance has the flag correctly set.
        # We don't need to check the concurrency check functionality, it is tested
        # elsewhere already.
        self.assertTrue(input_handler_instance_mock.skip_concurrency_check)

    @patch('simpleline.render.screen.input_manager.InputHandler')
    def test_uiscreen_non_blocking_input_disable_concurrency_check(self, input_handler_class_mock):
        # Replace default InputHandler instance created by InputManager by our mock to have
        # it stored after use.
        input_handler_instance_mock = InputHandlerMock()
        input_handler_class_mock.return_value = input_handler_instance_mock

        screen = UIScreen()
        input_manager = screen.input_manager
        input_manager.skip_concurrency_check = True
        screen.get_input_with_error_check("test")

        self.assertTrue(screen.input_manager.skip_concurrency_check)
        # Check that the created InputHandler instance has the flag correctly set.
        # We don't need to check the concurrency check functionality, it is tested
        # elsewhere already.
        self.assertTrue(input_handler_instance_mock.skip_concurrency_check)

    @patch('simpleline.render.screen.input_manager.InputHandler')
    def test_uiscreen_default_concurrency_check(self, input_handler_class_mock):
        # Replace default InputHandler instance created by InputManager by our mock to have
        # it stored after use.
        input_handler_instance_mock = InputHandlerMock()
        input_handler_class_mock.return_value = input_handler_instance_mock

        screen = UIScreen()
        screen.get_user_input("test")

        self.assertFalse(screen.input_manager.skip_concurrency_check)
        # Check that the created InputHandler instance has the flag correctly set.
        # We don't need to check the concurrency check functionality, it is tested
        # elsewhere already.
        self.assertFalse(input_handler_instance_mock.skip_concurrency_check)


@patch('simpleline.input.input_handler.InputHandlerRequest._get_input')
@patch('sys.stdout', new_callable=StringIO)
class AdvWidgets_TestCase(unittest.TestCase, UtilityMixin):
    def setUp(self):
        self.correct_input = False
        self.args_used = False

    def test_gettext(self, stdout_mock, stdin_mock):
        prompt = "Type input"
        input_text = "user input"
        screen = GetInputScreen(message=prompt)
        stdin_mock.return_value = input_text

        self.schedule_screen_and_run(screen)

        expected_output = self.create_output_with_separators(["%s: " % prompt]).rstrip('\n')

        self.assertEqual(expected_output, stdout_mock.getvalue())
        self.assertEqual(screen.value, input_text)

    def test_gettext_with_condition(self, stdout_mock, stdin_mock):
        prompt = "Type input"
        wrong_input = "wrong"
        condition = lambda x, _: x != wrong_input
        stdin_mock.side_effect = self.input_generator()

        screen = GetInputScreen(message=prompt)
        screen.add_acceptance_condition(condition)

        self.schedule_screen_and_run(screen)

        temp_prompt = ["%s: %s: " % (prompt, prompt)]
        expected_output = self.create_output_with_separators(temp_prompt).rstrip("\n")

        self.assertEqual(expected_output, stdout_mock.getvalue())
        self.assertTrue(self.correct_input)

    def test_gettext_with_condition_and_use_arg(self, stdout_mock, stdin_mock):
        prompt = "Type input"
        user_input = "y"
        stdin_mock.return_value = user_input

        screen = GetInputScreen(message=prompt)
        screen.add_acceptance_condition(self.acceptance_condition_test, "y")

        self.schedule_screen_and_run(screen)

        expected_msg = "%s: " % prompt
        expected_output = self.create_output_with_separators([expected_msg]).rstrip("\n")

        self.assertEqual(expected_output, stdout_mock.getvalue())
        self.assertTrue(self.args_used)

    @patch("simpleline.global_configuration.GlobalConfiguration.password_function")
    def test_getpass(self, hiden_stdin_mock, stdout_mock, stdin_mock):
        prompt = "Type input"
        input_text = "user input"
        screen = GetPasswordInputScreen(message=prompt)
        hiden_stdin_mock.return_value = input_text

        self.schedule_screen_and_run(screen)

        self.assertEqual(screen.value, input_text)

    @patch("simpleline.global_configuration.GlobalConfiguration.password_function")
    def test_getpass_with_condition(self, hiden_stdin_mock, stdout_mock, stdin_mock):
        prompt = "Type input"
        wrong_input = "wrong"
        condition = lambda x, _: x != wrong_input
        hiden_stdin_mock.side_effect = self.input_generator()

        screen = GetPasswordInputScreen(message=prompt)
        screen.add_acceptance_condition(condition)

        self.schedule_screen_and_run(screen)

        self.assertTrue(self.correct_input)

    def input_generator(self):
        for i in ("wrong", "correct"):
            if i == "correct":
                self.correct_input = True
            yield i

    def acceptance_condition_test(self, user_input, args):
        if user_input == args:
            self.args_used = True
        return True
