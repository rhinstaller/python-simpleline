# Widgets test classes.
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


import unittest
from io import StringIO
from unittest.mock import patch

from simpleline import App
from simpleline.render.prompt import Prompt
from simpleline.render.screen import UIScreen
from simpleline.render.widgets import TextWidget, SeparatorWidget, CheckboxWidget, CenterWidget, ColumnWidget, \
                                      EntryWidget


class BaseWidgets_TestCase(unittest.TestCase):
    """Base class containing helper functions."""
    def setUp(self):
        self.w1 = TextWidget(u"Můj krásný dlouhý text")
        self.w2 = TextWidget(u"Test")
        self.w3 = TextWidget(u"Test 2")
        self.w4 = TextWidget(u"Krásný dlouhý text podruhé")
        self.w5 = TextWidget(u"Test 3")
        self.w6 = TextWidget("The rescue environment will now attempt "
                             "to find your Linux installation and mount it under "
                             "the directory : bla.  You can then make any changes "
                             "required to your system.  Choose '1' to proceed with "
                             "this step.\nYou can choose to mount your file "
                             "systems read-only instead of read-write by choosing "
                             "'2'.\nIf for some reason this process does not work "
                             "choose '3' to skip directly to a shell.\n\n")
        self.w7 = TextWidget("Wrapping toooooooooooooooooooooooooooooooooooooooooooo"
                             "oooooooooooooooooooooooooooooooooooooooooooooooooooooo long word.")
        self.w8 = TextWidget("Text that would be wrapped exactly at the screen width should"
                             " have special test. This one.")

    def evaluate_result(self, test_result, expected_result):
        self.assertEqual(len(test_result), len(expected_result))
        for i in range(0, len(test_result)):
            self.assertEqual(test_result[i], expected_result[i])


class Widgets_TestCase(BaseWidgets_TestCase):

    def test_separator_widget(self):
        w = SeparatorWidget()
        w.render(80)

        res_lines = w.get_lines()

        expected_result = [u""]

        self.evaluate_result(res_lines, expected_result)

    def test_separator_widget_multiline(self):
        w = SeparatorWidget(3)
        w.render(80)

        res_lines = w.get_lines()

        expected_result = [u"",
                           u"",
                           u""]

        self.evaluate_result(res_lines, expected_result)

    def test_column_widget(self):
        # Test column text
        c = ColumnWidget([(20, [self.w1, self.w2, self.w3]),
                          (25, [self.w4, self.w5]),
                          (15, [self.w1, self.w2, self.w3])], spacing=3)
        c.render(80)
        res_lines = c.get_lines()

        expected_result = [u"Můj krásný dlouhý      Krásný dlouhý text          Můj krásný",
                           u"text                   podruhé                     dlouhý text",
                           u"Test                   Test 3                      Test",
                           u"Test 2                                             Test 2"]
        self.evaluate_result(res_lines, expected_result)

    def test_column_wrapping(self):
        # Test column wrapping text
        c = ColumnWidget([(15, [self.w1, self.w2, self.w3]), (10, [self.w4, self.w5])], spacing=1)
        c.render(80)

        expected_result = [u"Můj krásný      Krásný",
                           u"dlouhý text     dlouhý",
                           u"Test            text",
                           u"Test 2          podruhé",
                           u"                Test 3"]

        res_lines = c.get_lines()
        self.evaluate_result(res_lines, expected_result)

    def test_multiline_text(self):
        self.w6.render(80)
        expected_result =[
            "The rescue environment will now attempt to find your Linux installation and",
            "mount it under the directory : bla.  You can then make any changes required to",
            "your system.  Choose '1' to proceed with this step.",
            "You can choose to mount your file systems read-only instead of read-write by",
            "choosing '2'.",
            "If for some reason this process does not work choose '3' to skip directly to a",
            "shell.",
            "",
            ""]
        res_lines = self.w6.get_lines()
        self.evaluate_result(res_lines, expected_result)

    def test_wrapping(self):
        # wrap long text
        self.w7.render(80)
        expected_result = [
            "Wrapping toooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
            "oooooooooooooooooooooooooooo long word."]
        res_lines = self.w7.get_lines()

        self.assertEqual(len(res_lines), len(expected_result))
        for i in range(0, len(res_lines)):
            self.assertEqual(res_lines[i], expected_result[i])

        self.w8.render(80)
        expected_result = ["Text that would be wrapped exactly at the screen width should have special test.",
                           "This one."]
        res_lines = self.w8.get_lines()

        self.evaluate_result(res_lines, expected_result)

    def test_checkbox(self):
        checkbox = CheckboxWidget(title="Test Title", text="Description")

        checkbox.render(80)

        expected_result = [u"[ ] Test Title",
                           u"    (Description)"]

        self.evaluate_result(checkbox.get_lines(), expected_result)

    def test_completed_checkbox(self):
        checkbox = CheckboxWidget(title="Title", text="Description", completed=True)

        checkbox.render(80)

        expected_result = [u"[x] Title",
                           u"    (Description)"]

        self.evaluate_result(checkbox.get_lines(), expected_result)

    def test_key_checkbox(self):
        checkbox = CheckboxWidget(key="o", title="Title", text="Description", completed=True)

        checkbox.render(80)

        expected_result = [u"[o] Title",
                           u"    (Description)"]

        self.evaluate_result(checkbox.get_lines(), expected_result)

    def test_empty_checkbox(self):
        checkbox = CheckboxWidget()

        checkbox.render(80)

        expected_result = [u"[ ]"]

        self.evaluate_result(checkbox.get_lines(), expected_result)

    def test_checkbox_wrapping(self):
        checkbox = CheckboxWidget(title="Title", text="Testing\nwrapping")

        checkbox.render(80)

        expected_result = [u"[ ] Title",
                           u"    (Testing",
                           u"    wrapping)"]

        self.evaluate_result(checkbox.get_lines(), expected_result)

    def test_center_widget(self):
        w = CenterWidget(self.w2)

        w.render(10)

        expected_result = [u"   Test"]

        self.evaluate_result(w.get_lines(), expected_result)

    def test_entry_widget(self):
        title = "Title"
        value = "Value"
        w = EntryWidget(title=title, value=value)

        w.render(30)

        expected_result = [title,
                           value]

        self.evaluate_result(w.get_lines(), expected_result)

    def test_entry_too_long(self):
        title = "Title too long"
        value = "Value also too long"
        w = EntryWidget(title=title, value=value)

        w.render(10)

        expected_result = [u"Title too",
                           u"long",
                           u"Value also",
                           u"too long"]

        self.evaluate_result(w.get_lines(), expected_result)

    def test_entry_value_empty(self):
        title = "Title"
        w = EntryWidget(title=title)

        w.render(20)

        expected_result = [title]

        self.evaluate_result(w.get_lines(), expected_result=expected_result)


@patch('simpleline.input.input_handler.InputHandlerRequest._get_input')
@patch('sys.stdout', new_callable=StringIO)
class WidgetProcessing_TestCase(unittest.TestCase):

    def _calculate_spacer(self):
        # this calculation is taken from scheduler for default width '80'
        return '\n'.join(2 * [80 * '='])

    def _expected_output(self, text, widget_height=20):

        # two lines are always added to the printed size
        prompt_height = 2
        real_widget_height = widget_height - prompt_height

        lines = text.split('\n')

        # add Press ENTER... to the text
        if len(lines) - 1 >= real_widget_height:
            lines.insert(real_widget_height, "\nPress %s to continue: \n" % Prompt.ENTER)

        msg = self._calculate_spacer() + '\n'
        msg += "\n".join(lines)
        msg += "\n"
        return msg

    def test_draw_simple_widget(self, out_mock, in_mock):
        widget_text = "Test"
        screen = ScreenWithWidget(widget_text)

        App.initialize()
        App.get_scheduler().schedule_screen(screen)
        App.run()

        self.assertEqual(self._expected_output(widget_text), out_mock.getvalue())

    def test_widget_multiline(self, out_mock, in_mock):
        widget_text = "Testing output\n\n\nAgain..."
        screen = ScreenWithWidget(widget_text)

        App.initialize()
        App.get_scheduler().schedule_screen(screen)
        App.run()

        self.assertEqual(self._expected_output(widget_text), out_mock.getvalue())

    def test_widget_too_high(self, out_mock, in_mock):
        in_mock.return_value = "\n"
        in_mock.side_effect = lambda: print('\n')

        widget_text = ("Line\n"
                       "Line2\n"
                       "Line3\n"
                       "Line4\n"
                       "Line5")
        # Screen height take into account also 2 lines for prompt
        screen = ScreenWithWidget(widget_text, height=6)

        App.initialize()
        App.get_scheduler().schedule_screen(screen)
        App.run()

        self.assertEqual(self._expected_output(widget_text, widget_height=6), out_mock.getvalue())

    def test_widget_is_exactly_height_to_print(self, out_mock, in_mock):
        widget_text = ("Line\n"
                       "Line2\n"
                       "Line3\n"
                       "Line4")
        # Screen height take into account also 2 lines for prompt
        screen = ScreenWithWidget(widget_text, height=6)

        App.initialize()
        App.get_scheduler().schedule_screen(screen)
        App.run()

        self.assertEqual(self._expected_output(widget_text, widget_height=6), out_mock.getvalue())


class ScreenWithWidget(UIScreen):

    def __init__(self, msg, height=25):
        super().__init__(screen_height=height)
        self._msg = msg
        self.input_required = False

    def refresh(self, args=None):
        super().refresh(args)
        self.window.add(TextWidget(self._msg))

    def show_all(self):
        super().show_all()
        self.close()
