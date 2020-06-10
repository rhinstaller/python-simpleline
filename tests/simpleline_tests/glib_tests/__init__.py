# Helper functions for the GLib test classes.
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

from simpleline import App
from simpleline.event_loop.glib_event_loop import GLibEventLoop

import gi
gi.require_version("GLib", "2.0")

from gi.repository import GLib


class GLibUtilityMixin(object):

    def __init__(self):
        self.loop = None
        self.timeout_error = False

    def _quit_loop(self, loop):
        """Kill GLib loop."""
        loop.quit()
        self.timeout_error = True
        return True

    def create_glib_loop(self):
        # clear flags
        self.timeout_error = False
        self.loop = GLibEventLoop()

        loop = self.loop.active_main_loop
        context = loop.get_context()

        # This is prevention from running loop indefinitely
        source = GLib.timeout_source_new_seconds(2)
        source.set_callback(self._quit_loop, loop)
        source.attach(context)

    def setup_glib(self):
        self.create_glib_loop()
        App.initialize(event_loop=self.loop)

    def teardown_glib(self):
        if self.timeout_error:
            raise AssertionError("Loop was killed by timeout!")

    def schedule_screen_and_run_with_glib(self, screen):
        self.setup_glib()

        App.get_scheduler().schedule_screen(screen)
        App.run()
