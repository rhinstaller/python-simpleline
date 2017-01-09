# -*- coding: utf-8 -*-

import unittest
from simpleline.base import App, UIScreen


class ScheduleScreen_TestCase(unittest.TestCase):
    def setUp(self):
        self.app = App("HelloWorld")

    def test_schedule_screen(self):
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

