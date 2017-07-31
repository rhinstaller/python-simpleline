# Class which serves shortcuts for UIScreen to schedule screens.
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
# Author(s): Jiri Konecny <jkonecny@redhat.com>
#

from simpleline.base import App


class SchedulerHandler(object):

    def schedule_screen(self, args=None):
        """Schedule screen to the active scheduler.

        See: `simpleline.render.screen_scheduler.schedule_screen()`.
        """
        App.get_scheduler().schedule_screen(ui_screen=self, args=args)

    def replace_screen(self, args=None):
        """Schedule screen to the active scheduler.

        See: `simpleline.render.screen_scheduler.replace_screen()`.
        """
        App.get_scheduler().replace_screen(ui_screen=self, args=args)

    def push_screen(self, args=None):
        """Schedule screen to the active scheduler.

        See: `simpleline.render.screen_scheduler.push_screen()`.
        """
        App.get_scheduler().push_screen(ui_screen=self, args=args)

    def push_screen_modal(self, args=None):
        """Schedule screen to the active scheduler.

        See: `simpleline.render.screen_scheduler.push_screen_modal()`.
        """
        App.get_scheduler().push_screen_modal(ui_screen=self, args=args)
