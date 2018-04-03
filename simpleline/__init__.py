# Library containing the Text UI framework.
#
# Base class for Simpleline Text UI framework.
#
# Copyright (C) 2016  Red Hat, Inc.
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

__all__ = ["App", "DEFAULT_WIDTH"]

DEFAULT_WIDTH = 80


class App(object):
    """This is the main class for Simpleline library.

    Do not create instance of this class. Use this class as static!
    The `initialize()` method must be called before use.

    It is giving you access to the scheduler and event loop. You can have only one instance of this
    class in your application.

    To create this instance call `App.initialize()` method. This method can also be used to
    reset settings in the App class to start with new event loop or scheduler.
    """
    __app = None

    class AppPimpl(object):

        def __init__(self, scheduler, event_loop, width):
            self.event_loop = event_loop
            self.scheduler = scheduler
            self.width = width

    @classmethod
    def initialize(cls, scheduler=None, event_loop=None, width=DEFAULT_WIDTH):
        """Create app instance inside of this class.

        This method can be called multiple times to reset App settings.

        :param scheduler: scheduler used for rendering screens; if not specified use
                         `simpleline.render.screen_scheduler.ScreenScheduler`.
        :type scheduler: instance of `simpleline.render.screen_scheduler.ScreenScheduler`.

        :param event_loop: event loop used for asynchronous tasks;
                           if not specified use `simpleline.event_loop.main_loop.MainLoop`.
        :type event_loop: object based on class `simpleline.event_loop.AbstractEventLoop`.
        """
        from simpleline.event_loop.main_loop import MainLoop
        from simpleline.render.screen_scheduler import ScreenScheduler

        if event_loop is None:
            event_loop = MainLoop()
        if scheduler is None:
            scheduler = ScreenScheduler(event_loop)

        cls.__app = cls.AppPimpl(scheduler, event_loop, width)

        cls._post_init()

    @classmethod
    def _post_init(cls):
        from simpleline.input.input_threading import InputThreadManager
        # FIXME: This should be done by more general way not by calling exact class here.
        # Create new instance of InputThreadManager because it needs new event loop
        InputThreadManager.create_new_instance()

    @classmethod
    def is_initialized(cls):
        """Is the App already initialized?

        :returns: True if the `App.initialized()` method was called, False otherwise.
        """
        if cls.__app is None:
            return False
        else:
            return True

    @classmethod
    def get_scheduler(cls):
        """Get instance of class responsible for rendering of the screen."""
        return cls.__app.scheduler

    @classmethod
    def get_event_loop(cls):
        """Get instance of class responsible for processing asynchronous events."""
        return cls.__app.event_loop

    @classmethod
    def set_width(cls, width):
        """Set width of the application."""
        cls.__app.width = width

    @classmethod
    def get_width(cls):
        """Get width of the application."""
        return cls.__app.width

    @classmethod
    def run(cls):
        """Run event loop.

        This is shortcut to `App.event_loop().run()`.
        """
        App.get_event_loop().run()
