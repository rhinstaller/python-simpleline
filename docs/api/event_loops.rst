.. _event_loops_label:

Event Loops
===========

.. currentmodule:: simpleline.event_loop

Event loops are the heart of Simpleline. Every event loop is based on the
:class:`AbstractEventLoop`, and they all work with :ref:`signals <signals_label>`.
A signal is a message passed to the loop containing some information. Signals are passed to
an event loop by calling :meth:`AbstractEventLoop.enqueue_signal`. These signals are then
processed by calling :meth:`AbstractEventLoop.process_signals`. This method can be called by
an application developer manually or by the :meth:`AbstractEventLoop.run` method, which is
called by :meth:`App.run() <simpleline.App.run>` to start the Simpleline-based application.
When a signal is processed, all handlers attached to this signal are called. Signal handler
assignment is done by the :meth:`AbstractEventLoop.register_signal_handler` method.

Event loops can also be started recursively by :meth:`AbstractEventLoop.execute_new_loop`.
The old event loop is waiting for this event loop to stop. New loop execution is mandatory for
modal screens to work, since they can't be interrupted by other screens. This new event
loop is terminated by closing the last screen in the event loop or by calling
the :meth:`AbstractEventLoop.close_loop` method.

The last event loop should be terminated by closing the last screen in the screen stack or by
calling :meth:`AbstractEventLoop.close_loop`. In case a fatal error occurs the
:meth:`AbstractEventLoop.force_quit` method can be used to immediately kill the loop.

If a reaction on quitting the application (closing the last event loop) is required, the quit
callback can be used. The quit callback can be set by
the :meth:`AbstractEventLoop.set_quit_callback` method.

The following event loops are supported by Simpleline, but you can also
:ref:`Create_your_own_loop_label` :

* :ref:`MainLoop_label`
* :ref:`GLib_Event_loop_label`

.. _MainLoop_label:

Main Loop
---------

The main loop is the default event loop for Simpleline projects. The benefit of using
:class:`MainLoop <main_loop.MainLoop>` is that it isn't necessary to have any dependencies on
other libraries. It is a lightweight event loop implemented completely in Python.

.. autoclass:: simpleline.event_loop.main_loop.MainLoop
    :members:
    :inherited-members:
    :show-inheritance:

.. _GLib_Event_loop_label:

GLib Event loop
---------------

The GLib event loop was added in order to utilize existing event loops used by other libraries,
for example, DBus connections. Simpleline with this loop should have the same behavior as with
the :ref:`MainLoop_label`.

To use this loop you need to set it via the :class:`App <simpleline.App>` class::

    # Create Glib event loop.
    glib_loop = GLibEventLoop()

    # Use glib event loop instead of the original one.
    # Everything else should behave the same as with the original Simpleline loop.
    App.initialize(event_loop=glib_loop)

The GLib loop can be accessed by the
:attr:`GLibEventLoop.active_main_loop <simpleline.event_loop.glib_event_loop.GLibEventLoop.active_main_loop>`
property, or by getting the default loop from GLib directly
`GLib.MainLoop() <https://developer.gnome.org/glib/stable/glib-The-Main-Event-Loop.html>`_.

.. autoclass:: simpleline.event_loop.glib_event_loop.GLibEventLoop
    :members:
    :inherited-members:
    :show-inheritance:

.. _Create_your_own_loop_label:

Create your own loop
--------------------

If new loop support is required, it should inherit from :class:`AbstractEventLoop` and
implement the same behavior as the :ref:`MainLoop_label`. You can use existing tests from the
event loops to start. If the new loop is stable enough, pull requests are always welcome at
`Simpleline repository <https://github.com/rhinstaller/python-simpleline>`_.

.. autoclass:: simpleline.event_loop.AbstractEventLoop
    :members:
    :inherited-members:
