# Containers test classes.
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

from tests.widgets_test import BaseWidgets_TestCase

from simpleline.render.containers import WindowContainer, ListRowContainer, ListColumnContainer, KeyPattern
from simpleline.render.widgets import TextWidget


class Containers_TestCase(BaseWidgets_TestCase):

    def _test_callback(self, data):
        pass

    def test_listrow_container(self):
        c = ListRowContainer(columns=2, items=[self.w2, self.w3, self.w5], columns_width=10, spacing=2, numbering=False)
        c.render(25)

        expected_result = [u"Test        Test 2",
                           u"Test 3"]
        res_lines = c.get_lines()

        self.evaluate_result(res_lines, expected_result)

    def test_empty(self):
        c = ListRowContainer(columns=1)

        c.render(10)
        result = c.get_lines()

        self.assertEqual(len(result), 0)

    def test_more_columns_than_widgets(self):
        c = ListRowContainer(columns=3, items=[self.w1], columns_width=40, numbering=False)
        c.render(80)

        expected_result = [u"Můj krásný dlouhý text"]

        res_lines = c.get_lines()
        self.evaluate_result(res_lines, expected_result)

    def test_listrow_wrapping(self):
        # spacing is 3 by default
        c = ListRowContainer(2, [self.w1, self.w2, self.w3, self.w4], columns_width=15, numbering=False)
        c.render(25)

        expected_result = [u"Můj krásný        Test",
                           u"dlouhý text",
                           u"Test 2            Krásný dlouhý",
                           u"                  text podruhé"]
        res_lines = c.get_lines()
        self.evaluate_result(res_lines, expected_result)

    def test_newline_wrapping(self):
        widgets = [TextWidget("Hello"), TextWidget("Wrap\nthis\ntext"), TextWidget("Hi"),
                   TextWidget("Hello2")]

        c = ListRowContainer(3, widgets, columns_width=6, spacing=1, numbering=False)
        c.render(80)

        expected_result = [u"Hello  Wrap   Hi",
                           u"       this",
                           u"       text",
                           u"Hello2"]
        res_lines = c.get_lines()
        self.evaluate_result(res_lines, expected_result)

    def test_listcolumn_container(self):
        c = ListColumnContainer(columns=2, items=[self.w2, self.w3, self.w5], columns_width=10, spacing=2,
                                numbering=False)
        c.render(25)

        expected_result = [u"Test        Test 3",
                           u"Test 2"]
        res_lines = c.get_lines()
        self.evaluate_result(res_lines, expected_result)

    def test_listcolumn_wrapping(self):
        # spacing is 3 by default
        c = ListColumnContainer(2, [self.w1, self.w2, self.w3, self.w4], columns_width=15, numbering=False)
        c.render(25)

        expected_result = [u"Můj krásný        Test 2",
                           u"dlouhý text",
                           u"Test              Krásný dlouhý",
                           u"                  text podruhé"]
        res_lines = c.get_lines()
        self.evaluate_result(res_lines, expected_result)

    def test_add_new_container(self):
        c = ListRowContainer(columns=2, items=[TextWidget("Ahoj")], columns_width=15, spacing=0, numbering=False)

        expected_result = [u"Ahoj"]

        c.render(80)
        self.evaluate_result(c.get_lines(), expected_result)

        c.add(TextWidget("Nový widget"))
        c.add(TextWidget("Hello"))

        expected_result = [u"Ahoj           Nový widget",
                           u"Hello"]

        c.render(80)
        self.evaluate_result(c.get_lines(), expected_result)

    def test_column_numbering(self):
        # spacing is 3 by default
        c = ListColumnContainer(2, [self.w1, self.w2, self.w3, self.w4], columns_width=16)
        c.render(25)

        expected_result = [u"1) Můj krásný      3) Test 2",
                           u"   dlouhý text",
                           u"2) Test            4) Krásný dlouhý",
                           u"                      text podruhé"]
        res_lines = c.get_lines()
        self.evaluate_result(res_lines, expected_result)

    def test_row_numbering(self):
        # spacing is 3 by default
        c = ListRowContainer(2, [self.w1, self.w2, self.w3, self.w4], columns_width=16)
        c.render(25)

        expected_result = [u"1) Můj krásný      2) Test",
                           u"   dlouhý text",
                           u"3) Test 2          4) Krásný dlouhý",
                           u"                      text podruhé"]
        res_lines = c.get_lines()
        self.evaluate_result(res_lines, expected_result)

    def test_custom_numbering(self):
        # spacing is 3 by default
        c = ListRowContainer(2, [self.w1, self.w2, self.w3, self.w4], columns_width=20)
        c.key_pattern = KeyPattern("a {:d} a ")
        c.render(25)

        expected_result = [u"a 1 a Můj krásný       a 2 a Test",
                           u"      dlouhý text",
                           u"a 3 a Test 2           a 4 a Krásný dlouhý",
                           u"                             text podruhé"]
        res_lines = c.get_lines()
        self.evaluate_result(res_lines, expected_result)

    def test_window_container(self):
        c = WindowContainer(title="Test")

        c.add(TextWidget("Body"))
        c.render(10)

        expected_result = [u"Test",
                           u"",
                           u"Body"]

        res_lines = c.get_lines()
        self.evaluate_result(res_lines, expected_result)

    def test_window_container_with_multiple_items(self):
        c = WindowContainer(title="Test")

        c.add(TextWidget("Body"))
        c.add(TextWidget("Body second line"))
        c.render(30)

        expected_result = [u"Test",
                           u"",
                           u"Body",
                           u"Body second line"]

        res_lines = c.get_lines()
        self.evaluate_result(res_lines, expected_result)

    def test_window_container_wrapping(self):
        c = WindowContainer(title="Test")

        c.add(TextWidget("Body long line"))
        c.add(TextWidget("Body"))
        c.render(5)

        expected_result = [u"Test",
                           u"",
                           u"Body",
                           u"long",
                           u"line",
                           u"Body"]

        res_lines = c.get_lines()
        self.evaluate_result(res_lines, expected_result)

    def test_list_container_without_width(self):
        column_count = 3
        spacing_width = 3
        c = ListRowContainer(column_count, spacing=spacing_width, numbering=False)

        c.add(TextWidget("AAAA"))
        c.add(TextWidget("BBBB"))
        c.add(TextWidget("CCCCC"))  # this line is too long
        c.add(TextWidget("DDDD"))

        expected_col_width = 4
        expected_spacing_sum = 2 * spacing_width  # three columns so 2 spacing between them
        render_width = (column_count * expected_col_width) + expected_spacing_sum
        c.render(render_width)

        expected_result = [u"AAAA   BBBB   CCCC",
                           u"              C",
                           u"DDDD"]

        res_lines = c.get_lines()
        self.evaluate_result(res_lines, expected_result)

    def test_list_container_too_small(self):
        # to be able to render this container we need at least 11 width
        # 8 will take only spacing and then 1 for every column
        c = ListRowContainer(3, spacing=4, numbering=False)

        c.add(TextWidget("This can't be rendered."))
        c.add(TextWidget("Because spacing takes more space than maximal width."))
        c.add(TextWidget("Exception will raise."))

        with self.assertRaisesRegex(ValueError, "Columns width is too small."):
            c.render(10)

    def test_list_container_too_small_turn_off_numbering(self):
        # to be able to render this container we need 11 width + three times numbers (3 characters) = 20
        # 8 will take only spacing and then 1 for every column
        c = ListRowContainer(3, spacing=4, numbering=True)

        c.add(TextWidget("This can't be rendered."))
        c.add(TextWidget("Because spacing takes more space than maximal width."))
        c.add(TextWidget("Exception will raise with info to turn off numbering."))

        with self.assertRaisesRegex(ValueError, "Increase column width or disable numbering."):
            c.render(19)
