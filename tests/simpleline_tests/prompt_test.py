# Prompt test classes.
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


import unittest

from simpleline.render.prompt import Prompt


class Prompt_TestCase(unittest.TestCase):
    def test_prompt_message(self):
        p = Prompt()

        self.assertEqual(p.message, Prompt.DEFAULT_MESSAGE)

        p.set_message("Brand new message")
        self.assertEqual(p.message, "Brand new message")

        p.set_message(u"Žluťoučký kůň")
        self.assertEqual(p.message, u"Žluťoučký kůň")

        p2 = Prompt("Default prompt text")
        self.assertEqual(p2.message, "Default prompt text")

    def test_add_options(self):
        p = Prompt()

        # add new option
        p.add_option("R", "refresh")
        self.assertTrue("R" in p.options)
        self.assertEqual(p.options["R"], "refresh")

        # add option over the existing option should trigger warning message
        with self.assertLogs("simpleline", level="WARNING"):
            p.add_option("R", "another refresh")

        # update existing option
        p.update_option("R", "new refresh option")
        self.assertEqual(p.options["R"], "new refresh option")

        # update non existing option should trigger warning
        with self.assertLogs("simpleline", level="WARNING"):
            p.update_option("N", "non existing option")

        p = Prompt()
        p.add_option("N", "new option")
        # remove option
        ret = p.remove_option("N")
        self.assertFalse("N" in p.options)
        self.assertEqual(ret, "new option")

        # remove non-existing option
        ret = p.remove_option("non-existing")
        self.assertIsNone(ret)

    def _check_default_option(self, prompt, key, value):
        self.assertEqual(len(prompt.options), 1)
        self.assertEqual(prompt.options[key], value)

    def test_refresh_option(self):
        # refresh option
        p = Prompt()
        p.add_refresh_option()
        self._check_default_option(p, Prompt.REFRESH, Prompt.REFRESH_DESCRIPTION)

        # test add with description
        p = Prompt()
        p.add_refresh_option("Other refresh")
        self._check_default_option(p, Prompt.REFRESH, "Other refresh")

        # change existing description
        p.add_refresh_option("New refresh")
        self._check_default_option(p, Prompt.REFRESH, "New refresh")

    def test_continue_option(self):
        # continue option
        p = Prompt()
        p.add_continue_option()
        self._check_default_option(p, Prompt.CONTINUE, Prompt.CONTINUE_DESCRIPTION)

        # test add with description
        p = Prompt()
        p.add_continue_option("Other continue")
        self._check_default_option(p, Prompt.CONTINUE, "Other continue")

        # change existing description
        p.add_continue_option("New continue")
        self._check_default_option(p, Prompt.CONTINUE, "New continue")

    def test_quit_option(self):
        # quit option
        p = Prompt()
        p.add_quit_option()
        self._check_default_option(p, Prompt.QUIT, Prompt.QUIT_DESCRIPTION)

        # test add with description
        p = Prompt()
        p.add_quit_option("Other quit")
        self._check_default_option(p, Prompt.QUIT, "Other quit")

        # change existing description
        p.add_quit_option("New quit")
        self._check_default_option(p, Prompt.QUIT, "New quit")

    def test_help_option(self):
        # help option
        p = Prompt()
        p.add_help_option()
        self._check_default_option(p, Prompt.HELP, Prompt.HELP_DESCRIPTION)

        # test add with description
        p = Prompt()
        p.add_help_option("Other help")
        self._check_default_option(p, Prompt.HELP, "Other help")

        # change existing description
        p.add_help_option("New help")
        self._check_default_option(p, Prompt.HELP, "New help")
