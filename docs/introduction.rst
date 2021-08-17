Introduction
============

Simpleline is a text UI framework. Originally a part of the Anaconda installer project.

It is designed to be used with line-based machines and tools (e.g. serial console) so that
every new line it appended to the bottom of the screen. Printed lines are never rewritten!

How to use
----------

The best learning sources can be found in the
`examples directory <https://github.com/rhinstaller/python-simpleline/tree/master/examples>`_ in
the `GitHub repository <https://github.com/rhinstaller/python-simpleline>`_ and you can read the
:ref:`guide_label` section of this documentation. However, some basic usage of Simpleline will be
shown here too, to get an idea of how Simpleline works::

    from simpleline import App
    from simpleline.render.screen import UIScreen
    from simpleline.render.screen_handler import ScreenHandler
    from simpleline.render.widgets import TextWidget


    # UIScreen is the main building item for Simpleline. Every screen
    # which will user see should be inherited from UIScreen.
    class HelloWorld(UIScreen):

        def __init__(self):
            # Set title of the screen.
            super().__init__(title=u"Hello World")

        def refresh(self, args=None):
            # Fill the self.window attribute by the WindowContainer and set screen title as header.
            super().refresh()
            widget = TextWidget("Body text")
            self.window.add_with_separator(widget)


    if __name__ == "__main__":
        # Initialize application (create scheduler and event loop).
        App.initialize()

        # Create our screen.
        screen = HelloWorld()

        # Schedule screen to the screen scheduler.
        # This can be called only after App.initialize().
        ScreenHandler.schedule_screen(screen)

        # Run the application. You must have some screen scheduled
        # otherwise it will end in an infinite loop.
        App.run()

The output from the simple *Hello World* example above::

    $ ./run_example.sh 00_basic
    ================================================================================
    ================================================================================
    Hello World

    Body text

    Please make a selection from the above ['c' to continue, 'q' to quit, 'r' to
    refresh]:

If a user presses **r** and then **enter** to refresh, the same screen is printed again.
This will be printed to a monitor::

    $ ./run_example.sh 00_basic
    ================================================================================
    ================================================================================
    Hello World

    Body text

    Please make a selection from the above ['c' to continue, 'q' to quit, 'r' to
    refresh]: r
    ================================================================================
    ================================================================================
    Hello World

    Body text

    Please make a selection from the above ['c' to continue, 'q' to quit, 'r' to
    refresh]:

As you can see the whole screen is not rewritten -- only printed again on the bottom. This
is the expected behavior so the actual screen is always at the bottom but you can see the whole
history. This behavior makes working with line based machines and tools much easier.

Dependencies
------------

This is a Python3-only project. This code should not be difficult to migrate to Python2. However,
there is no need from the community, so it is only compatible with Python3 at the moment. No special
libraries are required to use this library. If you want to use glib event loop instead of the
original one you need to install glib and Python3 gobject introspection.

If you want to run tests (make ci), you need to install
`Pocketlint <https://github.com/rhinstaller/pocketlint>`_ and
`glib <https://developer.gnome.org/glib/>`_ with gobject introspection for
`Python3 <https://docs.python.org/3/index.html>`_.
