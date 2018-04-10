# App class test classes.
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
from unittest import mock

from simpleline import App
from simpleline.global_configuration import GlobalConfiguration
from simpleline.input.input_threading import InputThreadManager
from simpleline.render.screen_scheduler import ScreenScheduler
from simpleline.event_loop.main_loop import MainLoop


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
        App.initialize("init")
        App.run()
        self.assertTrue(run_mock.called)

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
