# Rendering screen test classes.
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

from simpleline import App
from simpleline.render import RenderUnexpectedError
from simpleline.render.screen import UIScreen, InputState
from tests.simpleline_tests import UtilityMixin


def _fake_input(queue_instance, prompt, hidden):
    queue_instance.put("a")


@mock.patch('sys.stdout', new_callable=StringIO)
class SeparatorPrinting_TestCase(unittest.TestCase, UtilityMixin):

    def setUp(self):
        App.initialize()

    def test_separator(self, stdout_mock):
        ui_screen = EmptyScreen()

        self.schedule_screen_and_run(ui_screen)

        self.assertEqual(self.calculate_separator(), stdout_mock.getvalue())

    def test_other_width_separator(self, stdout_mock):
        ui_screen = EmptyScreen()
        width = 60

        App.set_width(width)
        App.get_scheduler().io_manager.width = width
        App.get_scheduler().schedule_screen(ui_screen)
        App.run()

        self.assertEqual(self.calculate_separator(width), stdout_mock.getvalue())

    def test_zero_width_no_separator(self, stdout_mock):
        ui_screen = EmptyScreen()
        width = 0

        App.set_width(width)
        App.get_scheduler().io_manager.width = width
        App.get_scheduler().schedule_screen(ui_screen)
        App.run()

        self.assertEqual("\n\n", stdout_mock.getvalue())

    def test_no_separator_when_screen_setup_fails(self, stdout_mock):
        ui_screen = TestScreenSetupFail()

        App.initialize()
        App.get_scheduler().schedule_screen(ui_screen)
        App.run()

        self.assertEqual("", stdout_mock.getvalue())

    def test_no_separator(self, stdout_mock):
        print_text = "testing"
        screen = NoSeparatorScreen(print_text)

        self.schedule_screen_and_run(screen)
        self.schedule_screen_and_run(screen)

        expected_output = print_text + "\n" + print_text + "\n"

        self.assertEqual(expected_output, stdout_mock.getvalue())


class SimpleUIScreenFeatures_TestCase(unittest.TestCase):

    def test_close_screen(self):
        screen = UIScreen()

        App.initialize()
        App.get_scheduler().schedule_screen(screen)
        # Program will quit in close_screen when stack is empty
        App.get_scheduler().schedule_screen(UIScreen())
        screen.close()

    def test_close_screen_closed_from_other_source_error(self):
        App.initialize()
        App.get_scheduler().schedule_screen(UIScreen())
        with self.assertRaises(RenderUnexpectedError):
            App.get_scheduler().close_screen(closed_from=mock.MagicMock())

    def test_failed_screen_setup(self):
        screen = FailedSetupScreen()

        App.initialize()
        App.get_scheduler().schedule_screen(screen)
        App.run()


@mock.patch('sys.stdout', new_callable=StringIO)
class SimpleUIScreenProcessing_TestCase(unittest.TestCase, UtilityMixin):

    def setUp(self):
        self._default_separator = self.calculate_separator(80)

    def test_screen_event_loop_processing(self, _):
        ui_screen = EmptyScreen()

        self.schedule_screen_and_run(ui_screen)

        self.assertTrue(ui_screen.is_closed)

    def test_running_empty_loop(self, _):
        App.initialize()
        loop = App.get_event_loop()
        loop.process_signals()

    def test_screen_event_loop_processing_with_two_screens(self, _):
        first_screen = EmptyScreen()
        screen = EmptyScreen()

        App.initialize()
        App.get_scheduler().schedule_screen(first_screen)
        App.get_scheduler().schedule_screen(screen)
        App.run()

        self.assertTrue(first_screen)
        self.assertTrue(screen)

    def test_screen_title_rendering(self, stdout_mock):
        screen = NoInputScreen()
        screen.title = u"TestTitle"

        self.schedule_screen_and_run(screen)

        out = self._default_separator
        out += "TestTitle\n\n"
        self.assertEqual(stdout_mock.getvalue(), out)


@mock.patch('sys.stdout', new_callable=StringIO)
@mock.patch('simpleline.event_loop.AbstractEventLoop.kill_app_with_traceback')
class ScreenException_TestCase(unittest.TestCase, UtilityMixin):

    def setUp(self):
        self._force_quit_called = False

    # The original method calls sys.exit(1) so we don't need to test this functionality
    def force_quit_mock(self, signal, data=None):
        self._force_quit_called = True
        loop = App.get_event_loop()
        loop.force_quit()

    def test_raise_exception_in_refresh(self, mock_kill_app, _):
        screen = ExceptionTestScreen(ExceptionTestScreen.REFRESH)
        mock_kill_app.side_effect = self.force_quit_mock

        self.schedule_screen_and_run(screen)
        self.assertTrue(self._force_quit_called)

    def test_raise_exception_in_rendering(self, mock_kill_app, _):
        screen = ExceptionTestScreen(ExceptionTestScreen.REDRAW)
        mock_kill_app.side_effect = self.force_quit_mock

        self.schedule_screen_and_run(screen)
        self.assertTrue(self._force_quit_called)


@mock.patch('sys.stdout')
@mock.patch('simpleline.render.io_manager.InOutManager._get_input')
class InputProcessing_TestCase(unittest.TestCase):

    def _test_getpass(self, prompt):
        self.pass_prompt = prompt
        self.pass_called = True
        return "test"

    def setUp(self):
        self.pass_called = False
        self.pass_prompt = None

        App.initialize()

    def test_basic_input(self, input_mock, mock_stdout):
        input_mock.return_value = "a"
        screen = InputScreen()

        App.get_scheduler().schedule_screen(screen)
        App.run()

        self.assertTrue(screen.input_processed)

    def test_process_input_and_redraw(self, input_mock, mock_stdout):
        input_mock.return_value = "a"
        screen = InputStateRedrawScreen()

        App.get_scheduler().schedule_screen(screen)
        App.run()

        self.assertTrue(screen.refreshed)

    def test_process_input_and_close(self, input_mock, mock_stdout):
        input_mock.return_value = "a"
        screen = InputStateCloseScreen()

        App.get_scheduler().schedule_screen(screen)
        App.run()

        self.assertTrue(screen.input_processed)

    def test_quit_input(self, mock_stdin, mock_stdout):
        mock_stdin.return_value = "q"
        screen = UIScreen()

        App.get_scheduler().schedule_screen(screen)
        App.run()

    def test_continue_input(self, mock_stdin, mock_stdout):
        mock_stdin.return_value = "c"
        screen = UIScreen()
        screen2 = EmptyScreen()

        App.get_scheduler().schedule_screen(screen)
        App.get_scheduler().schedule_screen(screen2)
        App.run()

        self.assertTrue(screen.screen_ready)
        self.assertTrue(screen.screen_ready)

    def test_refresh_input(self, mock_stdin, mock_stdout):
        mock_stdin.return_value = "r"
        screen = RefreshTestScreen()

        App.get_scheduler().schedule_screen(screen)
        App.run()

        self.assertTrue(screen.input_processed)

    def test_refresh_on_input_error(self, mock_stdin, mock_stdout):
        mock_stdin.return_value = "q"
        threshold = 5
        screen = InputErrorTestScreen(threshold)

        App.get_scheduler().schedule_screen(screen)
        App.run()

        self.assertEqual(screen.render_counter, 2)
        self.assertEqual(screen.error_counter, threshold)

    def test_multiple_refresh_on_input_error(self, mock_stdin, mock_stdout):
        mock_stdin.return_value = "q"
        threshold = 12
        screen = InputErrorTestScreen(threshold)

        App.get_scheduler().schedule_screen(screen)
        App.run()

        self.assertEqual(screen.render_counter, 3)
        self.assertEqual(screen.error_counter, threshold)

    def test_input_no_prompt(self, mock_stdin, mock_stdout):
        screen = InputWithNoPrompt()

        App.get_scheduler().schedule_screen(screen)
        App.run()

        self.assertTrue(screen.prompt_entered)

    @mock.patch('simpleline.event_loop.main_loop.MainLoop.process_signals')
    def test_custom_getpass(self, mock_stdin, mock_stdout, process_signals):
        prompt = mock.MagicMock()

        App.get_scheduler().io_manager.set_pass_func(self._test_getpass)
        App.get_scheduler().io_manager.get_user_input(prompt=prompt, hidden=True)

        self.assertTrue(self.pass_called)
        self.assertEqual(self.pass_prompt.rstrip(), str(prompt))


# HELPER CLASSES

class EmptyScreen(UIScreen):

    def __init__(self):
        super().__init__()
        self.is_closed = False
        EmptyScreen.title = ""
        self.input_required = False

    def show_all(self):
        self.close()

    def closed(self):
        self.is_closed = True


class TestScreenSetupFail(UIScreen):

    def __init__(self):
        super().__init__()
        self.input_required = False

    def setup(self, args):
        super().setup(args)
        return False


class InputErrorTestScreen(UIScreen):

    def __init__(self, error_threshold=5):
        super().__init__()
        self.error_counter = 0
        self.render_counter = 0
        self._error_threshold = error_threshold

    def input(self, args, key):
        if self.error_counter == self._error_threshold:
            # let "q" propagate to quit
            return key
        else:
            self.error_counter += 1
            return InputState.DISCARDED

    def show_all(self):
        self.render_counter += 1


class InputWithNoPrompt(UIScreen):

    def __init__(self):
        super().__init__()
        self.prompt_entered = False
        self.input_required = True

    def prompt(self, args=None):
        self.prompt_entered = True
        self.close()
        # do not process input - it was processed here by user
        return None


class RefreshTestScreen(UIScreen):

    def __init__(self):
        super().__init__()
        self.input_processed = False

    def input(self, args, key):
        self.input_processed = True
        return key

    def refresh(self, args=None):
        super().refresh(args)
        if self.input_processed:
            self.close()
            self.input_required = False
        return


class FailedSetupScreen(UIScreen):

    def setup(self, args):
        super().setup(args)
        return False


class NoSeparatorScreen(UIScreen):

    def __init__(self, print_string):
        super().__init__()
        self.input_required = False
        self.no_separator = True
        self._print_string = print_string

    def show_all(self):
        print(self._print_string)
        self.close()


class NoInputScreen(UIScreen):

    def __init__(self):
        super().__init__()
        self.input_required = False

    def show_all(self):
        super().show_all()
        self.close()


class InputScreen(UIScreen):

    def __init__(self):
        super().__init__()
        self.input_processed = False

    def input(self, args, key):
        if key == "a":
            self.input_processed = True
        self.close()
        return InputState.PROCESSED


class InputStateCloseScreen(UIScreen):

    def __init__(self):
        super().__init__()
        self.input_processed = False

    def input(self, args, key):
        self.input_processed = not self.input_processed
        return InputState.PROCESSED_AND_CLOSE


class InputStateRedrawScreen(UIScreen):

    def __init__(self):
        super().__init__()
        self._refreshing = False
        self.refreshed = False

    def input(self, args, key):
        if not self._refreshing:
            self._refreshing = True
            return InputState.PROCESSED_AND_REDRAW
        else:
            self.refreshed = True
            return InputState.PROCESSED_AND_CLOSE


class ExceptionTestScreen(UIScreen):
    """Raising an exception in some place of processing."""

    REFRESH = 0
    REDRAW = 1

    def __init__(self, where):
        super().__init__()
        self._where = where
        self.input_required = False

    def refresh(self, args=None):
        super().refresh()
        if self._where == self.REFRESH:
            raise TestRefreshException("Refresh test exception happened!")

    def show_all(self):
        super().show_all()
        if self._where == self.REDRAW:
            raise TestRedrawException("Redraw test exception happened!")


class TestRefreshException(Exception):
    pass


class TestRedrawException(Exception):
    pass
