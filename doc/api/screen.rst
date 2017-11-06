UIScreen
========

.. automodule:: simpleline.render.screen

The base class for creating a new screen. :class:`UIScreen` is used for any user interaction.
:class:`UIScreen` uses :ref:`containers <containers_label>` and :ref:`widgets <widgets_label>`
to present information to a user, and the :meth:`UIScreen.input` method to get input from a user
to an application. Screens are pushed to the screen stack, which are then used to
communicate with a user. See the :ref:`screen handling <screen_handling_label>` section to find
out more.

The methods :meth:`UIScreen.redraw`, :meth:`UIScreen.close`, :meth:`UIScreen.emit` and
:meth:`UIScreen.create_and_emit` are asynchronous. These methods will create a signal which
is passed to the event loop for later processing.

**Beware**, methods :meth:`UIScreen.redraw` and :meth:`UIScreen.close` can lead to unexpected
behavior when multiple instances of these signals are emitted (methods are called multiple times).
This can even crash your application.

Lifecycle
---------

Every :class:`UIScreen` has a distinct lifecycle: *uninitialized*, *initialized*, *draw*,
*process input* and *closed*. If the screen has already been initialized
(it was *drawn* to a monitor) and will be shown again, then the screen skips
the *uninitialized* stage. The screen can cycle between *draw* and *process input* stages by
calling the :meth:`UIScreen.redraw` method after processing user input.

In case :meth:`UIScreen.redraw` won't be called and no new screen is pushed, or this screen
wasn't closed, then an application will stay in an infinite loop waiting for something to happen.
This is correct behavior because there could be something in an event loop which will
call :meth:`UIScreen.redraw` later.

Rendering widgets
-----------------

The :meth:`UIScreen.refresh` method is the most important part of the :class:`UIScreen`.
It contains preparations for rendering (creating widgets and adding them to containers).
The :meth:`UIScreen.refresh` method will be called before anything is drawn on a monitor.

The :attr:`UIScreen.window` attribute, which is the
:class:`WindowContainer <simpleline.render.containers.WindowContainer>` instance, contains
all items (widgets, containers) which are to be rendered by the screen.
A new :class:`WindowContainer <simpleline.render.containers.WindowContainer>` is created in the
:meth:`UIScreen.refresh` method for every screen redraw. The :attr:`UIScreen.title` attribute is
passed to the :attr:`WindowContainer.title <simpleline.render.containers.WindowContainer.title>`
property, and a developer can add :ref:`widgets <widgets_label>` and other
:ref:`containers <containers_label>` to present items to a user by calling
:meth:`WindowContainer.add() <simpleline.render.containers.WindowContainer.add>` or
:meth:`WindowContainer.add_with_separator() <simpleline.render.containers.WindowContainer.add_with_separator>`.
Multiple items can be added by calling these methods repeatedly.

When everything is prepared properly in the :meth:`UIScreen.refresh` method, it needs to be drawn
on the monitor for a user. This is handled by the :meth:`UIScreen.show_all` method. This method
works automatically, but it could also be useful for a developer, especially when the screen will
not process input. In this case, the :meth:`UIScreen.input` method is not called at all.
Developers can override this method and call the parent class's :meth:`UIScreen.show_all`,
which will handle drawing the screen and any additional processing.

Redrawing the screen can be invoked by the :meth:`UIScreen.redraw` method. However, this is
not processed immediately. Instead it will be added to the event loop and processed later, when the
loop is idle. Beware, after every :meth:`redraw <UIScreen.redraw>` call the input is processed
if not disabled, so if multiple redraw signals are emitted, than the application will
crash.

The :meth:`UIScreen.redraw` method is also invoked when a screen is
:ref:`pushed <push_screen_label>` to the stack.

User input processing
---------------------

If the screen shouldn't process user input, the :attr:`UIScreen.input_required` property needs
to be set to `False`. `True` is the default value for this property.

After everything is printed to a monitor, the :class:`UIScreen` will wait for user input.
For this purpose there is :meth:`UIScreen.input`, which is called when a user passes string input
to a screen. The screen needs to react upon user input and return one of the options from the
:class:`InputState` enum or the user input string.

To accept the user input, :attr:`InputState.PROCESSED` should be returned.
In this case the :class:`UIScreen` needs to :meth:`close <UIScreen.close>` the screen or
:meth:`redraw <UIScreen.redraw>` it, otherwise it will stay in an infinite loop.

In case the user input is invalid, the :attr:`InputState.DISCARDED` value should be returned.
This will reject the user input and wait for another attempt. The :class:`UIScreen.refresh`
method will be called after 5 rejections and show the screen output again.

If the user input string is returned it will be checked for
options of the :class:`Prompt <simpleline.render.prompt.Prompt>` instance which can either
close the screen, refresh the screen (this will call :meth:`UIScreen.refresh`)
or quit the application.

Closing screens
---------------

There are several ways to close a screen. One is by calling :meth:`UIScreen.close` or
by pressing *c* to continue (with the default
:class:`Prompt <simpleline.render.prompt.Prompt>` class). When the screen is closed
the next screen on the stack will be shown. A screen can also be
:ref:`replaced <replace_screen_label>`. Then the original screen is removed from the stack
without closing a screen. If a reaction on closing a screen is required then the
:meth:`UIScreen.closed` callback should be overridden.

**Beware**, when calling :meth:`UIScreen.close` multiple times it will close multiple screens.
This is because the close signal will always close the top screen on the screen stack.

UIScreen class
--------------

.. autoclass:: UIScreen
    :members:
    :inherited-members:

InputState enum
---------------

.. autoclass:: InputState
    :members:
    :undoc-members:
