# Screen scheduling GLib test classes.
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


from . import GLibUtilityMixin
from ..main.screen_scheduler_test import ScreenScheduler_TestCase


class GLibScreenScheduler_TestCase(ScreenScheduler_TestCase, GLibUtilityMixin):

    def tearDown(self):
        super().tearDown()
        self.teardown_glib()

    def schedule_screen_and_run(self, screen):
        self.schedule_screen_and_run_with_glib(screen)


# Hack to avoid running the original class thanks to import
del ScreenScheduler_TestCase
