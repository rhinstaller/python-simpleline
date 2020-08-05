# Serves shortcuts for easy screen scheduling.
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

from simpleline import App


class ScreenHandler():

    @classmethod
    def schedule_screen(cls, ui_screen, args=None):
        """Schedule screen to the active scheduler.

        See: `simpleline.render.screen_scheduler.schedule_screen()`.
        """
        App.get_scheduler().schedule_screen(ui_screen=ui_screen, args=args)

    @classmethod
    def replace_screen(cls, ui_screen, args=None):
        """Schedule screen to the active scheduler.

        See: `simpleline.render.screen_scheduler.replace_screen()`.
        """
        App.get_scheduler().replace_screen(ui_screen=ui_screen, args=args)

    @classmethod
    def push_screen(cls, ui_screen, args=None):
        """Schedule screen to the active scheduler.

        See: `simpleline.render.screen_scheduler.push_screen()`.
        """
        App.get_scheduler().push_screen(ui_screen=ui_screen, args=args)

    @classmethod
    def push_screen_modal(cls, ui_screen, args=None):
        """Schedule screen to the active scheduler.

        See: `simpleline.render.screen_scheduler.push_screen_modal()`.
        """
        App.get_scheduler().push_screen_modal(ui_screen=ui_screen, args=args)
