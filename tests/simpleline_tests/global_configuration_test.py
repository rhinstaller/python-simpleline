# GlobalConfiguration class test classes.
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
