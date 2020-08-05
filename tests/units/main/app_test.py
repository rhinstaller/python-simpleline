# App class test classes.
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

from unittest import mock

from simpleline import App
from simpleline.global_configuration import GlobalConfiguration
from simpleline.input.input_threading import InputThreadManager
from simpleline.render.screen_scheduler import ScreenScheduler
from simpleline.event_loop.main_loop import MainLoop
from simpleline.errors import NothingScheduledError


class App_TestCase(unittest.TestCase):

    def test_create_instance(self):
        App.initialize()
        self.assertTrue(isinstance(App.get_scheduler(), ScreenScheduler))
        self.assertTrue(isinstance(App.get_event_loop(), MainLoop))
        self.assertTrue(isinstance(App.get_configuration(), GlobalConfiguration))

    def test_create_instance_with_custom_scheduler(self):
        App.initialize(scheduler=CustomScreenScheduler(CustomEventLoop()))
        self.assertTrue(isinstance(App.get_scheduler(), CustomScreenScheduler))

    def test_create_instance_with_event_loop(self):
        App.initialize(event_loop=CustomEventLoop())
        self.assertTrue(isinstance(App.get_event_loop(), CustomEventLoop))

    def test_create_instance_with_configuration(self):
        App.initialize(global_configuration=CustomGlobalConfiguration())
        self.assertTrue(isinstance(App.get_configuration(), CustomGlobalConfiguration))

    def test_create_instance_with_custom_everything(self):
        event_loop = CustomEventLoop()
        App.initialize(event_loop=event_loop,
                       scheduler=CustomScreenScheduler(event_loop),
                       global_configuration=CustomGlobalConfiguration())

        self.assertTrue(isinstance(App.get_event_loop(), CustomEventLoop))
        self.assertTrue(isinstance(App.get_scheduler(), CustomScreenScheduler))
        self.assertTrue(isinstance(App.get_configuration(), CustomGlobalConfiguration))

    def test_reinitialize(self):
        event_loop1 = CustomEventLoop()
        event_loop2 = CustomEventLoop()
        scheduler1 = CustomScreenScheduler(event_loop1)
        scheduler2 = CustomScreenScheduler(event_loop2)
        configuration1 = CustomGlobalConfiguration()
        configuration2 = CustomGlobalConfiguration()

        App.initialize(event_loop=event_loop1, scheduler=scheduler1,
                       global_configuration=configuration1)
        self._check_app_settings(event_loop1, scheduler1, configuration1)

        App.initialize(event_loop=event_loop2, scheduler=scheduler2,
                       global_configuration=configuration2)
        self._check_app_settings(event_loop2, scheduler2, configuration2)

        App.initialize()
        self.assertNotEqual(App.get_event_loop(), event_loop2)
        self.assertNotEqual(App.get_scheduler(), scheduler2)
        self.assertNotEqual(App.get_configuration(), configuration2)

    def test_input_thread_manager_after_initialize(self):
        App.initialize()

        thread_mgr = InputThreadManager.get_instance()

        App.initialize()

        self.assertNotEqual(thread_mgr, InputThreadManager.get_instance())

    @mock.patch('simpleline.event_loop.main_loop.MainLoop.run')
    def test_run_shortcut(self, run_mock):
        App.initialize()
        App.get_configuration().should_run_with_empty_stack = True
        App.run()
        self.assertTrue(run_mock.called)

    def test_run_with_empty_screen_stack(self):
        App.initialize()
        with self.assertRaises(NothingScheduledError):
            App.run()

    def _check_app_settings(self, event_loop, scheduler, configuration):
        self.assertEqual(App.get_event_loop(), event_loop)
        self.assertEqual(App.get_scheduler(), scheduler)
        self.assertEqual(App.get_configuration(), configuration)


class CustomScreenScheduler(ScreenScheduler):
    pass


class CustomEventLoop(MainLoop):
    pass


class CustomGlobalConfiguration(GlobalConfiguration):
    pass
