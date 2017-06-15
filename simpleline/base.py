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

from simpleline.render.renderer import Renderer
from simpleline.event_loop.main_loop import MainLoop

__all__ = ["App", "UIScreen"]


class App(object):
    """This is the main class for Simpleline library.

    It giving you access to the renderer and event loop. You can have only one instance of this
    class in your application.

    To create this instance call `App.initialize()` method. This method can also be used to
    reset settings in the App class to start with new event loop or renderer.
    """
    __app = None

    class AppPimpl(object):

        def __init__(self, title, renderer, event_loop):
            self.header = title
            self.event_loop = event_loop
            self.renderer = renderer

    def __init__(self):
        """Do not create instance of this class. Use this class as static.

        The `initialize()` method must be called before use.
        """
        super().__init__()

    @classmethod
    def initialize(cls, title, renderer=None, event_loop=None):
        """Create app instance inside of this class.

        This method can be called multiple times to reset App settings.

        :param title: application title for whenever we need to display app name
        :type title: str

        :param renderer: renderer used for rendering screens; if not specified use `simpleline.render.renderer.Renderer`
        :type renderer: instance of `simpleline.render.renderer.Renderer`

        :param event_loop: event loop used for asynchronous tasks;
                           if not specified use `simpleline.event_loop.main_loop.MainLoop`
        :type event_loop: object based on class `simpleline.event_loop.AbstractEventLoop`
        """
        if event_loop is None:
            event_loop = MainLoop()
        if renderer is None:
            renderer = Renderer(event_loop)

        cls.__app = cls.AppPimpl(title, renderer, event_loop)

    @classmethod
    def header(cls):
        """Application title."""
        return cls.__app.header

    @classmethod
    def renderer(cls):
        """Get instance of class responsible for rendering of the screen."""
        return cls.__app.renderer

    @classmethod
    def event_loop(cls):
        """Get instance of class responsible for processing asynchronous events."""
        return cls.__app.event_loop

    @classmethod
    def run(cls):
        """Run event loop.

        This is shortcut to `App.event_loop().run()`.
        """
        App.event_loop().run()
