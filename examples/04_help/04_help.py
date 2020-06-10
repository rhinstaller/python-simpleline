#!/bin/python3
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

# Show help screen.
#
# Usage of the HelpScreen advanced widget.
# There are many of advanced widgets which have different uses.
# I've recommend developer to look on them.

from simpleline import App
from simpleline.render.screen_handler import ScreenHandler
from simpleline.render.adv_widgets import HelpScreen


if __name__ == "__main__":
    App.initialize()
    # You need to pass file with help text to the screen.
    s = HelpScreen("./04_help/example_help.txt")
    ScreenHandler.schedule_screen(s)
    App.run()
