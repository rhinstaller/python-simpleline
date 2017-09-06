# Event loop test classes for GLib implementation.
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

from tests.event_loop_test import ProcessEvents_TestCase
from tests.glib_tests import GLibUtilityMixin


class GLibProcessEvents_TestCase(ProcessEvents_TestCase, GLibUtilityMixin):
    """Run all the tests in ProcessEvents test case but with GLib event loop."""

    def tearDown(self):
        super().tearDown()
        self.teardown_glib()

    def create_loop(self):
        self.create_glib_loop()
