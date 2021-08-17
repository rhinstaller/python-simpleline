Errors module
=============

.. automodule:: simpleline.errors

Collection of generic exception classes used everywhere in the project. The most important one is
:class:`SimplelineError`, which is the base exception for all the other exceptions used in
the Simpleline project.

.. autoexception:: SimplelineError
    :members:
    :show-inheritance:

Render exceptions
-----------------

Exceptions used for rendering errors.


.. automodule:: simpleline.render

.. autoexception:: RenderError
    :members:
    :show-inheritance:

.. autoexception:: RenderUnexpectedError
    :members:
    :show-inheritance:

Event loop exceptions
---------------------

Exceptions used for errors in event loops.

.. automodule:: simpleline.event_loop

.. autoexception:: simpleline.event_loop.ExitMainLoop
    :members:
    :show-inheritance:
