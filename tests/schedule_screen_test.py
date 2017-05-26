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
        self.app.schedule_screen_with_args(screen, screen_argument)

        screen_data = self.app._screen_stack.pop(False)
        self.assertEqual(screen_data.ui_screen, screen)
        self.assertEqual(screen_data.args, screen_argument)
        self.assertEqual(screen_data.execute_loop, False)

        # test everything again but now add new screen
        # new screen will be first screen now
        screen2 = UIScreen(self.app)
        screen_argument2 = "test2"
        self.app.schedule_screen_with_args(screen2, screen_argument2)

        screen_data_old = self.app._screen_stack.pop()
        screen_data_new = self.app._screen_stack.pop()
        self.assertEqual(screen_data_old, screen_data)
        self.assertEqual(screen_data_new.ui_screen, screen2)
        self.assertEqual(screen_data_new.args, screen_argument2)
        self.assertEqual(screen_data_new.execute_loop, False)

    def test_switch_screen(self):
        """Test App.switch_screen() method"""
        old_screen = UIScreen(self.app)
        new_screen = UIScreen(self.app)

        self.app.schedule_screen(old_screen)
        old_loop = self.app._screen_stack.pop(False).execute_loop
        self.app.switch_screen(new_screen, "arguments")

        tested_screen = self.app._screen_stack.pop()
        self.assertEqual(tested_screen.ui_screen, new_screen)
        self.assertEqual(tested_screen.args, "arguments")
        self.assertEqual(tested_screen.execute_loop, old_loop)

    def test_switch_screen_with_return(self):
        """Test App.switch_screen_with_return() method"""
        old_screen = UIScreen(self.app)
        new_screen = UIScreen(self.app)

        self.app.schedule_screen(old_screen)
        self.app.switch_screen_with_return(new_screen, ["arguments"])

        # last screen in the stack should be the new one
        screen_data = self.app._screen_stack.pop()
        self.assertEqual(screen_data.ui_screen, new_screen)
        self.assertEqual(screen_data.args, ["arguments"])

        # old screen still should be there
        screen_data = self.app._screen_stack.pop().ui_screen
        self.assertEqual(screen_data, old_screen)

    @mock.patch('simpleline.base.App._do_redraw')
    def test_switch_screen_modal(self, redraw):
        """Test App.switch_screen_modal() method"""
        old_screen = UIScreen(self.app)
        new_screen = UIScreen(self.app)

        self.app.schedule_screen(old_screen)
        self.app.switch_screen_modal(new_screen, "arguments")

        tested_new_screen = self.app._screen_stack.pop()
        self.assertEqual(tested_new_screen.ui_screen, new_screen)
        self.assertEqual(tested_new_screen.args, "arguments")
        self.assertEqual(tested_new_screen.execute_loop, True)

        # old screen still should be here
        self.assertEqual(self.app._screen_stack.pop().ui_screen, old_screen)

