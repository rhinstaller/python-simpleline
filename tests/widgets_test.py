# -*- coding: utf-8 -*-

import unittest

from simpleline.render.widgets import TextWidget, ColumnWidget


class Widgets_TestCase(unittest.TestCase):
    def evaluate_result(self, test_result, expected_result):
        self.assertEqual(len(test_result), len(expected_result))
        for i in range(0, len(test_result)):
            self.assertEqual(test_result[i], expected_result[i])

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
            "shell."]
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

