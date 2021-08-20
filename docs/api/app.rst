App
===

.. automodule:: simpleline

The App class is the heart of Simpleline. It holds the :ref:`event loop <event_loops_label>`
instance and scheduler which are used by Simpleline. Both can be replaced if needed in the
initialization phase by calling the :meth:`App.initialize` method. However, by replacing the
scheduler you are replacing most of the logic in Simpleline. Replacing the scheduler is not
supported, since it is currently not a part of the public API.

All Simpleline applications must be run by the :meth:`App.run` method. This method will start
the event loop instance created in the initialization process.

If a reaction on application quit is required, please set
:meth:`set_quit_callback <event_loop.AbstractEventLoop.set_quit_callback>` in the used event loop.
This can be done by::

    loop = App.get_event_loop()
    loop.set_quit_callback(callback_function)

**Do not instantiate the** :class:`App` **class!** It is designed to be used in a purely static way.


Application configuration
-------------------------

Configuration of the application is saved in the
:class:`GlobalConfiguration <global_configuration.GlobalConfiguration>` class. This class can be
created before :meth:`App.initialize` is called and passed in as a
parameter. This way the same configuration can be used between re-initialization of the
application. The configuration can easily be changed, even while an application is running,
by setting desired properties.

Look at the :class:`GlobalConfiguration <global_configuration.GlobalConfiguration>` to find out
all the configuration possibilities.

App class
---------

.. autoclass:: App
    :members:

GlobalConfiguration class
-------------------------

.. autoclass:: simpleline.global_configuration.GlobalConfiguration
    :members:
