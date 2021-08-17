.. _screen_handling_label:

Screen Handling
===============

.. automodule:: simpleline.render.screen_handler

The :class:`ScreenHandler` class is used to schedule a
:class:`UIScreen <simpleline.render.screen.UIScreen>` to the screen stack.

Screen handling is an important part of using the Simpleline library, and it is recommended
for a developer to get familiar with this principle. Screen handling is the gateway by which
a developer manages the stack, by either adding or removing screens from it.
There are many ways to add a screen to the stack. To remove a screen from the stack, the screen
must be closed, or it can be replaced by another screen.
To close a :class:`UIScreen <simpleline.render.screen.UIScreen>` a developer should call
the :meth:`UIScreen.close() <simpleline.render.screen.UIScreen.close()>`
method. A screen can also be closed when a user presses `c` (which can be disabled). This will
close the screen automatically. When a screen is closed, the next screen on the top of
the stack will be rendered. If the stack is empty then the application will close.

**Do not instantiate the** :class:`ScreenHandler` **class!** All methods in the
:class:`ScreenHandler` class are class methods so the :class:`ScreenHandler` shouldn't be
instantiated at all.

The following operations can be used to schedule a screen.

Schedule screen
---------------

To schedule a screen use the :meth:`ScreenHandler.schedule_screen` method.
Scheduling a screen should be used on the first screen in your application before starting the
event loop. The screen is added to the bottom of the screen stack, and it will be visible as
the last screen in a stack.

This is the only way to add a screen to the screen stack without emitting a redraw call.

.. _push_screen_label:

Push screen
-----------

To push a screen to the stack use the :meth:`ScreenHandler.push_screen` method.
Pushing a screen to the stack will place a screen on top of the stack, so it will be
drawn on the next redraw call. The original screen will remain on the stack, so after the new
screen is closed, the original screen will be rendered again. If you need to avoid this behavior
please close the active screen before pushing a new screen to the stack.

The redraw signal will be emitted automatically when a screen is pushed.

.. _push_screen_modal_label:

Push screen as modal
--------------------

To push a modal screen to the stack use the :meth:`ScreenHandler.push_screen_modal` method.
This behaves the same as :ref:`push_screen_label` with one important difference. The pushed screen
will act as a modal screen. A modal screen has its own event loop, so event processing of the old
loop is blocked until the modal screen is closed. The code processing is also blocked by the
:meth:`ScreenHandler.push_screen_modal` method call.

The :meth:`UIScreen.redraw() <simpleline.render.screen.UIScreen.redraw>` method may be
required if the original screen was already drawn before invoking the
:meth:`ScreenHandler.push_screen_method` method.

The redraw signal will be emitted automatically when a screen is pushed.

.. _replace_screen_label:

Replace screen
--------------

Replace an existing screen with a new screen. This behaves like :ref:`push_screen_label` but it
replaces the original screen, so there is no need to close the original screen.

The redraw signal will be emitted automatically when a screen is replaced.

ScreenHandler class
-------------------

.. autoclass:: ScreenHandler
    :members:
