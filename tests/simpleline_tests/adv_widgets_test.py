# Advanced widgets test cases.
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
from unittest.mock import patch

from io import StringIO

from tests.simpleline_tests import UtilityMixin

from simpleline.render.adv_widgets import GetInputScreen


@patch('simpleline.render.io_manager.InOutManager._get_input')
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

        expected_output = self.create_output_with_separators(["%s: %s: " % (prompt, prompt)]).rstrip("\n")

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

    def input_generator(self):
        for i in ("wrong", "correct"):
            if i == "correct":
                self.correct_input = True
            yield i

    def acceptance_condition_test(self, user_input, args):
        if user_input == args:
            self.args_used = True
        return True
