# Rendering screen test classes for GLib implementation.
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


from tests.simpleline_tests.glib_tests import GLibUtilityMixin
from tests.simpleline_tests.render_screen_test import SimpleUIScreenProcessing_TestCase, \
    InputProcessing_TestCase, ScreenException_TestCase


class GLibSimpleUIScreenProcessing_TestCase(SimpleUIScreenProcessing_TestCase, GLibUtilityMixin):
    """Run all the tests in ProcessEvents test case but with GLib event loop."""

    def setUp(self):
        super().setUp()
        self.loop = None
        self.timeout_error = False

    def tearDown(self):
        super().tearDown()
        self.teardown_glib()

    def schedule_screen_and_run(self, screen):
        self.schedule_screen_and_run_with_glib(screen)


# Hack to avoid running the original class thanks to import
del SimpleUIScreenProcessing_TestCase


class GLibScreenException_TestCase(ScreenException_TestCase, GLibUtilityMixin):

    def tearDown(self):
        super().tearDown()
        self.teardown_glib()

    def schedule_screen_and_run(self, screen):
        self.schedule_screen_and_run_with_glib(screen)


# Hack to avoid running the original class thanks to import
del ScreenException_TestCase


class GLibInputProcessing_TestCase(InputProcessing_TestCase, GLibUtilityMixin):

    def setUp(self):
        super().setUp()
        self.setup_glib()

    def tearDown(self):
        super().tearDown()
        self.teardown_glib()


# Hack to avoid running the original class thanks to import
del InputProcessing_TestCase
