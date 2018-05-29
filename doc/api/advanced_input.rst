Advanced Input
==============

.. automodule:: simpleline.input.input_handler

.. WARNING::
    This section contains advanced input techniques which may lead to buggy code in your
    program if they are not used correctly.

The default technique to get user input is already described in :ref:`UIScreen <uiscreen_label>`,
and that should be the preferred way to obtain user input. However, if the default technique is
not enough for your situation then read the text below to find out how to implement custom input.

Input handler classes
---------------------
Input handler classes are classes created to obtain user input. If required
:class:`InputHandler` can block an application until user input is received.

This class can be instantiated everywhere in the code and used to ask for user input::

    handler = InputHandler()
    handler.get_input("Shut up and give me your input:")
    handler.wait_for_input()
    if handler.input_successful:
        user_input = handler.value

The :meth:`InputHandler.wait_on_input` method will block code processing until user input is
received. Input should always be checked before processing.

In case some other work needs to be done before user input is received, then pass
a callback to the constructor of the :class:`InputHandler` class and do not use
the :meth:`InputHandler.wait_on_input` method. However, the callback is using
the :ref:`event loop<event_loops_label>` so it won't be called until event loop
processing is active. If :ref:`concurrent input<concurrent_input_label>` is used then this
callback might never get called!

If what a user types must not be displayed, then the :class:`PasswordInputHandler` class
should be used. It shares most of its implementation with the :class:`InputHandler` but overrides
how to obtain the code. For more info look at the :class:`PasswordInputHandler` class
documentation.

.. _concurrent_input_label:

Concurrent input
----------------

Concurrent input is something which should be avoided. It drags unexpected behavior into an
application and is hard to debug. However, there could be an instance when user input is required
immediately, even when an application is already waiting for other input.

By default, every attempt for concurrent input will raise an exception and kill the application to
prevent unexpected behavior. In order to allow for concurrent input, the
:attr:`InputHandler.skip_concurrency_check` property must be set. After this property is disabled
for the :class:`InputHandler` instance, then the handler instance then it can support
concurrent input.

The last registered concurrent input will result in dropping all other waiting inputs -- even other
waiting inputs with :attr:`InputHandler.skip_concurrency_check` will be dropped. The dropped
waiting inputs will get a failed input signal to unblock :meth:`InputHandler.wait_on_input`
methods.


Creating a custom InputHandler
------------------------------

If the :class:`InputHandler` class or the :class:`PasswordInputHandler` class is not enough,
developers can create their own handler. The structure of an input handler is based on two
classes. First is a handler itself, and second is the request object it creates.

The handler class is used as an interface for the rest of the application. It also creates
the requester instance. The requester object is a low-level implementation of obtaining user input.
The requester object has to have the ``get_input`` method and should contain the ``text_prompt``
method. The ``get_input`` method is called in a separate thread and should prompt the user for
input. The ``text_prompt`` method is required mainly for concurrent input, and it returns
a string representation of the prompt.

For more details, please look at the implementation of the :class:`InputHandler` class.


InputHandler class
------------------

.. autoclass:: InputHandler
    :members:

PasswordInputHandler class
--------------------------

.. autoclass:: PasswordInputHandler
    :members:
    :inherited-members:

