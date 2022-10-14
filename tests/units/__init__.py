# Helper functions for the test classes.
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
from simpleline.global_configuration import DEFAULT_WIDTH


class UtilityMixin():

    @staticmethod
    def calculate_separator(width=DEFAULT_WIDTH):
        separator = "\n".join(2 * [width * "="])
        separator += "\n"  # print adds another newline
        return separator

    def create_output_with_separators(self, screens_text):
        msg = ""
        for screen_txt in screens_text:
            msg += self.calculate_separator()
            msg += screen_txt + "\n\n"

        return msg

    def schedule_screen_and_run(self, screen):
        App.initialize()
        App.get_scheduler().schedule_screen(screen)
        App.run()
