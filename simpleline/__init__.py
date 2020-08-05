# Base class for Simpleline Text UI framework.
#
# Library containing the Text UI framework.
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

__all__ = ["App"]


from simpleline.logging import setup_logging
from simpleline.errors import NothingScheduledError

setup_logging()


class App():
    """This is the main class for Simpleline library.

    Do not create instance of this class. Use this class as static!
    The `initialize()` method must be called before use.

    It is giving you access to the scheduler and event loop. You can have only one instance of this
    class in your application.

    To create this instance call `App.initialize()` method. This method can also be used to
    reset settings in the App class to start with new event loop or scheduler.
    """
    __app = None

    class AppPimpl():

        def __init__(self, scheduler, event_loop, configuration):
            self.event_loop = event_loop
            self.scheduler = scheduler
            self.configuration = configuration

    @classmethod
    def initialize(cls, scheduler=None, event_loop=None, global_configuration=None):
        """Create app instance inside of this class.

        This method can be called multiple times to reset App settings.

        :param scheduler: scheduler used for rendering screens; if not specified use
                         `simpleline.render.screen_scheduler.ScreenScheduler`.
        :type scheduler: instance of `simpleline.render.screen_scheduler.ScreenScheduler`.

        :param event_loop: event loop used for asynchronous tasks;
                           if not specified use `simpleline.event_loop.main_loop.MainLoop`.
        :type event_loop: object based on class `simpleline.event_loop.AbstractEventLoop`.

        :param global_configuration: instance of the global configuration object; if not specified
                                     use `simpleline.global_configuration.GlobalConfiguration`
        :type global_configuration: object based on class
                                    `simpleline.global_configuration.GlobalConfiguration`
        """
        from simpleline.event_loop.main_loop import MainLoop # pylint: disable=import-outside-toplevel
        from simpleline.render.screen_scheduler import ScreenScheduler # pylint: disable=import-outside-toplevel
        from simpleline.global_configuration import GlobalConfiguration # pylint: disable=import-outside-toplevel

        if event_loop is None:
            event_loop = MainLoop()
        if scheduler is None:
            scheduler = ScreenScheduler(event_loop)
        if global_configuration is None:
            global_configuration = GlobalConfiguration()

        cls.__app = cls.AppPimpl(scheduler, event_loop, global_configuration)

        cls._post_init()

    @classmethod
    def _post_init(cls):
        from simpleline.input.input_threading import InputThreadManager # pylint: disable=import-outside-toplevel
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
    def get_configuration(cls):
        """Get application defaults configuration object."""
        return cls.__app.configuration

    @classmethod
    def run(cls):
        """Run event loop.

        Raise an exception if no screen is scheduled. This behavior can be changed by
        `should_run_with_empty_stack` global configuration option.

        This is shortcut to `App.event_loop().run()`.
        :raises NothingScheduledError: when there is no screen scheduled
        """
        if not cls.__app.configuration.should_run_with_empty_stack:
            # Check if the screen stack is not empty
            if cls.__app.scheduler.nothing_to_render:
                raise NothingScheduledError("Can't run application with the empty screen stack! "
                                            "To avoid this please see should_run_with_empty_stack "
                                            "global configuration option.")
        App.get_event_loop().run()
