# Event loop test classes for GLib implementation.
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

from tests.simpleline_tests.event_loop_test import ProcessEvents_TestCase
from tests.simpleline_tests.glib_tests import GLibUtilityMixin


class GLibProcessEvents_TestCase(ProcessEvents_TestCase, GLibUtilityMixin):
    """Run all the tests in ProcessEvents test case but with GLib event loop."""

    def tearDown(self):
        super().tearDown()
        self.teardown_glib()

    def create_loop(self):
        self.create_glib_loop()


# Hack to avoid running the original class thanks to import
del ProcessEvents_TestCase
