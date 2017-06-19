import unittest
from unittest import mock
from io import StringIO

from simpleline.base import App
from simpleline.render.ui_screen import UIScreen
from simpleline.render import INPUT_PROCESSED


def _calculate_separator(width):
    separator = "\n".join(2 * [width * "="])
    separator += "\n"  # print adds another newline
    return separator


def _schedule_screen_and_run(screen):
    App.initialize("Test")
    App.renderer().schedule_screen(screen)
    App.run()


def _fake_input(queue_instance, prompt, hidden):
    queue_instance.put("a")


@mock.patch('sys.stdout', new_callable=StringIO)
class SeparatorPrinting_TestCase(unittest.TestCase):

    def test_separator(self, stdout_mock):
        ui_screen = EmptyScreen()

        _schedule_screen_and_run(ui_screen)

        self.assertEqual(stdout_mock.getvalue(), _calculate_separator(80))

    def test_other_width_separator(self, stdout_mock):
        ui_screen = EmptyScreen()
        width = 60

        App.initialize("Test")
        App.renderer().width = width
        App.renderer().schedule_screen(ui_screen)
        App.run()

        self.assertEqual(stdout_mock.getvalue(), _calculate_separator(width))

    def test_no_separator(self, stdout_mock):
        ui_screen = EmptyScreen()
        width = 0

        App.initialize("Test")
        App.renderer().width = width
        App.renderer().schedule_screen(ui_screen)
        App.run()

        self.assertEqual(stdout_mock.getvalue(), "\n\n")


@mock.patch('sys.stdout', new_callable=StringIO)
class SimpleUIScreenProcessing_TestCase(unittest.TestCase):

    def setUp(self):
        self._default_separator = _calculate_separator(80)

    def test_screen_event_loop_processing(self, _):
        ui_screen = EmptyScreen()

        _schedule_screen_and_run(ui_screen)

        self.assertTrue(ui_screen.is_closed)

    def test_screen_event_loop_processing_with_two_screens(self, _):
        first_screen = EmptyScreen()
        screen = EmptyScreen()

        App.initialize("Test")
        App.renderer().schedule_screen(first_screen)
        App.renderer().schedule_screen(screen)
        App.run()

        self.assertTrue(first_screen)
        self.assertTrue(screen)

    def test_screen_title_rendering(self, stdout_mock):
        screen = NoInputScreen()
        screen.title = u"TestTitle"

        _schedule_screen_and_run(screen)

        out = self._default_separator
        out += "TestTitle\n\n"
        self.assertEqual(stdout_mock.getvalue(), out)

    @mock.patch('simpleline.render.renderer.Renderer.raw_input')
    def test_basic_input(self, input_mock, _):
        input_mock.return_value = "a"
        screen = InputScreen()

        _schedule_screen_and_run(screen)

        self.assertTrue(screen.input_processed)


@mock.patch('sys.stdout', new_callable=StringIO)
class ScreenScheduler_TestCase(unittest.TestCase):

    def test_replace_screen(self, _):
        replace_screen = ShowedCounterScreen()
        screen = ShowedCounterScreen(replace_screen=replace_screen)

        _schedule_screen_and_run(screen)

        self.assertEqual(screen.counter, 1)
        self.assertEqual(replace_screen.counter, 1)

    def test_switch_screen(self, _):
        switched_screen = ShowedCounterScreen()
        screen = ShowedCounterScreen(switched_screen)

        _schedule_screen_and_run(screen)

        self.assertEqual(screen.counter, 2)
        self.assertEqual(switched_screen.counter, 1)

    def test_switch_screen_modal_in_render(self, _):
        modal_screen = ModalTestScreen()
        screen = ModalTestScreen(modal_screen_render=modal_screen)

        _schedule_screen_and_run(screen)

        self.assertEqual(screen.copied_modal_counter, ModalTestScreen.AFTER_MODAL_START_RENDER)
        self.assertEqual(modal_screen.copied_modal_counter, ModalTestScreen.BEFORE_MODAL_START_RENDER)

    def test_switch_screen_modal_in_refresh(self, _):
        modal_screen = ModalTestScreen()
        screen = ModalTestScreen(modal_screen_refresh=modal_screen)

        _schedule_screen_and_run(screen)

        self.assertEqual(screen.copied_modal_counter, ModalTestScreen.AFTER_MODAL_START_REFRESH)
        self.assertEqual(modal_screen.copied_modal_counter, ModalTestScreen.BEFORE_MODAL_START_REFRESH)

    def test_switch_screen_modal_refresh_and_render(self, _):
        modal_refresh = ModalTestScreen()
        modal_render = ModalTestScreen()
        screen = ModalTestScreen(modal_screen_refresh=modal_refresh, modal_screen_render=modal_render)

        _schedule_screen_and_run(screen)

        self.assertEqual(screen.copied_modal_counter, ModalTestScreen.AFTER_MODAL_START_RENDER)
        self.assertEqual(modal_refresh.copied_modal_counter, ModalTestScreen.BEFORE_MODAL_START_REFRESH)
        self.assertEqual(modal_render.copied_modal_counter, ModalTestScreen.BEFORE_MODAL_START_RENDER)

    def test_switch_screen_modal_render_recursive(self, _):
        modal_render_inner = ModalTestScreen()
        modal_render_outer = ModalTestScreen(modal_screen_render=modal_render_inner)
        screen = ModalTestScreen(modal_screen_render=modal_render_outer)

        _schedule_screen_and_run(screen)

        self.assertEqual(screen.copied_modal_counter, ModalTestScreen.AFTER_MODAL_START_RENDER)
        # outer modal screen has AFTER_MODAL_START_RENDER because it was set before by inner loop
        self.assertEqual(modal_render_outer.copied_modal_counter, ModalTestScreen.AFTER_MODAL_START_RENDER)
        self.assertEqual(modal_render_inner.copied_modal_counter, ModalTestScreen.BEFORE_MODAL_START_RENDER)


@mock.patch('sys.stdout', new_callable=StringIO)
class ScreenException_TestCase(unittest.TestCase):

    def test_raise_exception_in_refresh(self, _):
        screen = ExceptionTestScreen(ExceptionTestScreen.REFRESH)

        with self.assertRaises(TestRefreshException):
            _schedule_screen_and_run(screen)

    def test_raise_exception_in_rendering(self, _):
        screen = ExceptionTestScreen(ExceptionTestScreen.REDRAW)

        with self.assertRaises(TestRedrawException):
            _schedule_screen_and_run(screen)


class EmptyScreen(UIScreen):

    def __init__(self):
        super().__init__()
        self.is_closed = False

    def refresh(self, args=None):
        super().refresh(args)
        self.close()
        # Do not ask for input
        return False

    def closed(self):
        self.is_closed = True


class NoInputScreen(UIScreen):

    def refresh(self, args=None):
        super().refresh(args)
        # Do not ask for input
        return False

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
        return INPUT_PROCESSED


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


class ExceptionTestScreen(UIScreen):
    """Raising an exception in some place of processing."""

    REFRESH = 0
    REDRAW = 1

    def __init__(self, where):
        super().__init__()
        self._where = where

    def refresh(self, args=None):
        super().refresh()
        if self._where == self.REFRESH:
            raise TestRefreshException("Refresh test exception happened!")
        return False

    def show_all(self):
        super().show_all()
        if self._where == self.REDRAW:
            raise TestRedrawException("Redraw test exception happened!")


class TestRefreshException(Exception):
    pass


class TestRedrawException(Exception):
    pass
