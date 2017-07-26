# Base class for Simpleline Text UI framework.
#
# Copyright (C) 2016, 2017  Red Hat, Inc.
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
# Author(s): Jiri Konecny <jkonecny@redhat.com>
#

from simpleline.render.screen_scheduler import ScreenScheduler
from simpleline.event_loop.main_loop import MainLoop

__all__ = ["App"]


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

        def __init__(self, scheduler, event_loop):
            self.event_loop = event_loop
            self.scheduler = scheduler

    @classmethod
    def initialize(cls, scheduler=None, event_loop=None):
        """Create app instance inside of this class.

        This method can be called multiple times to reset App settings.

        :param scheduler: scheduler used for rendering screens; if not specified use
                         `simpleline.render.screen_scheduler.ScreenScheduler`.
        :type scheduler: instance of `simpleline.render.screen_scheduler.ScreenScheduler`.

        :param event_loop: event loop used for asynchronous tasks;
                           if not specified use `simpleline.event_loop.main_loop.MainLoop`.
        :type event_loop: object based on class `simpleline.event_loop.AbstractEventLoop`.
        """
        if event_loop is None:
            event_loop = MainLoop()
        if scheduler is None:
            scheduler = ScreenScheduler(event_loop)

        cls.__app = cls.AppPimpl(scheduler, event_loop)

    @classmethod
    def get_scheduler(cls):
        """Get instance of class responsible for rendering of the screen."""
        return cls.__app.scheduler

    @classmethod
    def get_event_loop(cls):
        """Get instance of class responsible for processing asynchronous events."""
        return cls.__app.event_loop

    @classmethod
    def run(cls):
        """Run event loop.

        This is shortcut to `App.event_loop().run()`.
        """
        App.get_event_loop().run()
