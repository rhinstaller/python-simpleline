# Screen scheduling test classes.
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
from unittest import mock

from simpleline.base import App
from simpleline.render.screen import UIScreen
from tests import schedule_screen_and_run, create_output_with_separators


@mock.patch('sys.stdout', new_callable=StringIO)
class ScreenScheduler_TestCase(unittest.TestCase):

    def test_replace_screen(self, _):
        replace_screen = ShowedCounterScreen()
        screen = ShowedCounterScreen(replace_screen=replace_screen)

        schedule_screen_and_run(screen)

        self.assertEqual(screen.counter, 1)
        self.assertEqual(replace_screen.counter, 1)

    def test_switch_screen(self, _):
        switched_screen = ShowedCounterScreen()
        screen = ShowedCounterScreen(switched_screen)

        schedule_screen_and_run(screen)

        self.assertEqual(screen.counter, 2)
        self.assertEqual(switched_screen.counter, 1)

    def test_switch_screen_modal_in_render(self, _):
        modal_screen = ModalTestScreen()
        screen = ModalTestScreen(modal_screen_render=modal_screen)

        schedule_screen_and_run(screen)

        self.assertEqual(screen.copied_modal_counter, ModalTestScreen.AFTER_MODAL_START_RENDER)
        self.assertEqual(modal_screen.copied_modal_counter, ModalTestScreen.BEFORE_MODAL_START_RENDER)

    def test_switch_screen_modal_in_refresh(self, _):
        modal_screen = ModalTestScreen()
        screen = ModalTestScreen(modal_screen_refresh=modal_screen)

        schedule_screen_and_run(screen)

        self.assertEqual(screen.copied_modal_counter, ModalTestScreen.AFTER_MODAL_START_REFRESH)
        self.assertEqual(modal_screen.copied_modal_counter, ModalTestScreen.BEFORE_MODAL_START_REFRESH)

    def test_switch_screen_modal_refresh_and_render(self, _):
        modal_refresh = ModalTestScreen()
        modal_render = ModalTestScreen()
        screen = ModalTestScreen(modal_screen_refresh=modal_refresh, modal_screen_render=modal_render)

        schedule_screen_and_run(screen)

        self.assertEqual(screen.copied_modal_counter, ModalTestScreen.AFTER_MODAL_START_RENDER)
        self.assertEqual(modal_refresh.copied_modal_counter, ModalTestScreen.BEFORE_MODAL_START_REFRESH)
        self.assertEqual(modal_render.copied_modal_counter, ModalTestScreen.BEFORE_MODAL_START_RENDER)

    def test_switch_screen_modal_render_recursive(self, _):
        modal_render_inner = ModalTestScreen()
        modal_render_outer = ModalTestScreen(modal_screen_render=modal_render_inner)
        screen = ModalTestScreen(modal_screen_render=modal_render_outer)

        schedule_screen_and_run(screen)

        self.assertEqual(screen.copied_modal_counter, ModalTestScreen.AFTER_MODAL_START_RENDER)
        # outer modal screen has AFTER_MODAL_START_RENDER because it was set before by inner loop
        self.assertEqual(modal_render_outer.copied_modal_counter, ModalTestScreen.AFTER_MODAL_START_RENDER)
        self.assertEqual(modal_render_inner.copied_modal_counter, ModalTestScreen.BEFORE_MODAL_START_RENDER)

    @mock.patch('simpleline.render.io_manager.InOutManager.get_user_input')
    def test_switch_screen_modal_input_order(self, mock_input, mock_stdout):
        modal_screen = InputAndDrawScreen("Modal")
        parent_screen = EmitDrawThenCreateModal(modal_screen, msg="Parent")
        mock_input.return_value = "c"
        expected = ["Modal",  # modal needs to be printed first
                    "Parent",   # draw enqueued draw signal -- manually registered in refresh()
                    "Parent"]   # draw because modal screen was closed

        schedule_screen_and_run(parent_screen)

        self.maxDiff = None
        self.assertEqual(create_output_with_separators(expected), mock_stdout.getvalue())


class ShowedCounterScreen(UIScreen):

    def __init__(self, switch_to_screen=None, replace_screen=None):
        super().__init__()
        self._switch_to_screen = switch_to_screen
        self._replace_screen = replace_screen
        self.counter = 0

    def refresh(self, args=None):
        super().refresh(args)
        return False

    def show_all(self):
        super().show_all()
        self.counter += 1
        if self._switch_to_screen is not None:
            App.renderer().switch_screen(self._switch_to_screen)
            self._switch_to_screen = None
        elif self._replace_screen is not None:
            App.renderer().replace_screen(self._replace_screen)
            self._replace_screen = None
        else:
            self.close()


class ModalTestScreen(UIScreen):
    """Test if the modal screen is really modal and stops the execution in a place where we start the modal screen.

    This class have checkpoints which increment class variable counter. This counter is copied in the modal instance
    to the local variable self.copied_modal_counter.
    In the end we should check if the instance modal counter have the correct value, which is before the
    modal screen was started (1).
    """

    INIT = 0
    BEFORE_MODAL_START_REFRESH = 1
    AFTER_MODAL_START_REFRESH = 2
    BEFORE_MODAL_START_RENDER = 3
    AFTER_MODAL_START_RENDER = 4

    modal_counter = 0

    def __init__(self, modal_screen_render=None, modal_screen_refresh=None):
        super().__init__()
        self._modal_screen_render = modal_screen_render
        self._modal_screen_refresh = modal_screen_refresh
        self.copied_modal_counter = 0
        ModalTestScreen.modal_counter = self.INIT

    def refresh(self, args=None):
        super().refresh(args)
        if self._modal_screen_refresh is not None:
            # Start a new modal screen
            ModalTestScreen.modal_counter = self.BEFORE_MODAL_START_REFRESH
            App.renderer().switch_screen_modal(self._modal_screen_refresh)
            ModalTestScreen.modal_counter = self.AFTER_MODAL_START_REFRESH
        return False

    def show_all(self):
        super().show_all()
        if self._modal_screen_render is not None:
            # Start new modal screen
            ModalTestScreen.modal_counter = self.BEFORE_MODAL_START_RENDER
            App.renderer().switch_screen_modal(self._modal_screen_render)
            ModalTestScreen.modal_counter = self.AFTER_MODAL_START_RENDER

        self.copied_modal_counter = ModalTestScreen.modal_counter
        self.close()


class EmitDrawThenCreateModal(UIScreen):

    def __init__(self, refresh_screen, msg):
        super().__init__()
        self._refresh_screen = refresh_screen
        self.title = msg

    def refresh(self, args=None):
        super().refresh(args)
        self.redraw()
        if self._refresh_screen:
            App.renderer().switch_screen_modal(self._refresh_screen)
            self._refresh_screen = None
        return True


class InputAndDrawScreen(UIScreen):

    def __init__(self, msg):
        super().__init__()
        self.title = msg

    def refresh(self, args=None):
        super().refresh(args)
        return True
