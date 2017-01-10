# -*- coding: utf-8 -*-

import unittest
from unittest import mock
from simpleline.base import App, UIScreen


class ScheduleScreen_TestCase(unittest.TestCase):
    def setUp(self):
        self.app = App("HelloWorld")

    def test_schedule_screen(self):
        """Test App.schedule_screen() method"""
        # test if everything is set up correctly when screen is scheduled before App start
        screen = UIScreen(self.app)
        screen_argument = "test"
        self.app.schedule_screen(screen, screen_argument)

        self.assertEqual(len(self.app._screens), 1)
        self.assertEqual(len(self.app._screens[0]), 3)
        self.assertEqual(self.app._screens[0][0], screen)
        self.assertEqual(self.app._screens[0][1], screen_argument)
        self.assertEqual(self.app._screens[0][2], self.app.NOP)

        # test everything again but now add new screen
        # new screen will be first screen now
        screen2 = UIScreen(self.app)
        screen_argument2 = "test2"
        self.app.schedule_screen(screen2, screen_argument2)

        self.assertEqual(len(self.app._screens), 2)
        self.assertEqual(len(self.app._screens[0]), 3)
        self.assertEqual(self.app._screens[0][0], screen2)
        self.assertEqual(self.app._screens[0][1], screen_argument2)
        self.assertEqual(self.app._screens[0][2], self.app.NOP)

    def test_switch_screen(self):
        """Test App.switch_screen() method"""
        old_screen = UIScreen(self.app)
        new_screen = UIScreen(self.app)

        self.app.schedule_screen(old_screen)
        oldloop = self.app._screens[-1][2]
        self.app.switch_screen(new_screen, "arguments")

        self.assertEqual(self.app._screens[0][0], new_screen)
        self.assertEqual(self.app._screens[0][1], "arguments")
        self.assertEqual(self.app._screens[0][2], oldloop)

    def test_switch_screen_with_return(self):
        """Test App.switch_screen_with_return() method"""
        old_screen = UIScreen(self.app)
        new_screen = UIScreen(self.app)

        self.app.schedule_screen(old_screen)
        self.app.switch_screen_with_return(new_screen, "arguments")

        # old screen still should be there
        self.assertEqual(self.app._screens[0][0], old_screen)
        # last screen in the stack should be the new one
        self.assertEqual(self.app._screens[1][0], new_screen)
        self.assertEqual(self.app._screens[1][1], "arguments")

    @mock.patch('simpleline.base.App._do_redraw')
    def test_switch_screen_modal(self, redraw):
        """Test App.switch_screen_modal() method"""
        old_screen = UIScreen(self.app)
        new_screen = UIScreen(self.app)

        self.app.schedule_screen(old_screen)
        self.app.switch_screen_modal(new_screen, "arguments")

        # old screen still should be here
        self.assertEqual(self.app._screens[0][0], old_screen)
        self.assertEqual(self.app._screens[1][0], new_screen)
        self.assertEqual(self.app._screens[1][1], "arguments")
        self.assertEqual(self.app._screens[1][2], App.START_MAINLOOP)
