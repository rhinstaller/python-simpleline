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

# Usage of base widgets.
#
# Show base widgets for user interaction in one screen.
#

from simpleline import App
from simpleline.render.screen import UIScreen
from simpleline.render.screen_handler import ScreenHandler
from simpleline.render.widgets import TextWidget, CenterWidget, CheckboxWidget


class HelloWorld(UIScreen):

    def __init__(self):
        # Set title of the screen.
        super().__init__(title=u"Show Widgets")

    def refresh(self, args=None):
        super().refresh()

        # Text widget
        # Show text to user. This is basic widget which will handle
        # wrapping of words for you.
        text_widget = TextWidget("Text widget")
        self.window.add_with_separator(text_widget)

        # Center widget
        # Wrap extisting widget and center it to the middle of the screen.
        text = TextWidget("Center widget")
        center_widget = CenterWidget(text)
        self.window.add_with_separator(center_widget, blank_lines=3)  # Add two more blank lines

        # Checkbox widget
        # Checkbox which can hold 2 states.
        checkbox_widget = CheckboxWidget(key="o",
                                         title="Checkbox title",
                                         text="Checkbox text",
                                         completed=True)
        self.window.add_with_separator(checkbox_widget)

        # Checkbox widget unchecked
        checkbox_widget_unchecked = CheckboxWidget(key="o",
                                                   title="Checkbox title",
                                                   text="Unchecked",
                                                   completed=False)
        self.window.add_with_separator(checkbox_widget_unchecked)


if __name__ == "__main__":
    App.initialize()

    screen = HelloWorld()
    ScreenHandler.schedule_screen(screen)

    App.run()
