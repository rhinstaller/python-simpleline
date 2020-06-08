# GlobalConfiguration class test classes.
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

from unittest.mock import MagicMock

from simpleline import App
from simpleline.global_configuration import DEFAULT_WIDTH, DEFAULT_PASSWORD_FUNC


class GlobalConfiguration_TestCase(unittest.TestCase):

    def tearDown(self):
        App.initialize()

    def _check_default_width(self, width=DEFAULT_WIDTH):
        self.assertEqual(App.get_configuration().width, width)

    def _check_default_password_function(self, password_func=None):
        if password_func:
            self.assertEqual(App.get_configuration().password_function, password_func)
        else:
            self.assertEqual(App.get_configuration().password_function, DEFAULT_PASSWORD_FUNC)

    def test_clear_width(self):
        self._check_default_width()

        test_width = 150

        App.get_configuration().width = test_width
        self._check_default_width(test_width)

        App.get_configuration().clear_width()
        self._check_default_width()

    def test_width(self):
        self._check_default_width()

        App.initialize()
        App.get_configuration().width = 100
        self._check_default_width(100)

        App.initialize()
        self._check_default_width()

    def test_password_function(self):
        self._check_default_password_function()

        test_mock = MagicMock()
        App.initialize()
        App.get_configuration().password_function = test_mock
        self._check_default_password_function(test_mock)

        App.initialize()
        self._check_default_password_function()

    def test_clear_password_function(self):
        self._check_default_password_function()

        test_func = MagicMock()

        App.get_configuration().password_function = test_func
        self._check_default_password_function(test_func)

        App.get_configuration().clear_password_function()
        self._check_default_password_function()
