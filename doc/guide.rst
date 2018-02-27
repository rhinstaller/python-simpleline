.. _guide_label:

Guide to Simpleline
===================

Simpleline is a text user interface framework written completely in Python 3 with a possibility to
have :ref:`non-python event loops <event_loops_label>`. With the exception of optional event loops,
Simpleline has almost no dependency on external libraries.

This UI is simple and easy to use. It is designed to be used with line-based machines and tools
(e.g. serial console) so that every new line is appended to the bottom of the screen.
Printed lines are never rewritten!

Basic components
----------------

For every application, the following parts are always required.

* The :class:`App <simpleline.App>` static class to initialize and run application.
* The :class:`ScreenHandler <simpleline.render.screen_handler.ScreenHandler>` static class for
  scheduling screens.
* The :class:`UIScreen <simpleline.render.screen.UIScreen>` based classes to create screens which
  will form the application.
* :ref:`Widgets <widgets_label>` to show anything on the screens.
* :ref:`Containers <containers_label>` to position widgets on the screen.

Look at the next section to see how everything fits together.

How to create a simple application
----------------------------------

.. currentmodule:: simpleline.render.screen

Interaction with a user is necessary to have a useful UI framework. To show anything to a user the
:class:`UIScreen` class must be used. So we will subclass this class to create our screen and set
a title for it::

    class DividerScreen(UIScreen):

        def __init__(self):
            # Set title of the screen.
            super().__init__(title=u"Divider")
            self._message = 0

The ``self._message`` variable will be used later to show results to the user.

The screen's main purpose is to present content to a user. For this we need widgets and containers.

The :attr:`UIScreen.window` attribute is the most important part of the screen for rendering.
It contains the :class:`WindowContainer <simpleline.render.containers.WindowContainer>`
container which is created and filled up by the :meth:`UIScreen.refresh` method.
Everything added to this container is printed to the monitor.
We should override the :meth:`UIScreen.refresh` method and call the parent's version to
prepare the container. Then we can add :ref:`widgets <widgets_label>` to the container.
The screen will continue like this:

.. code-block:: python
    :dedent: 0

        def refresh(self, args=None):
            # Fill the self.window attribute by the WindowContainer and set screen title as header.
            super().refresh()

            widget = TextWidget("Result: " + str(self._message))
            self.window.add_with_separator(widget)

The :meth:`WindowContainer.add_with_separator() <simpleline.render.containers.WindowContainer.add_with_separator>`
method will print a blank line after the
:class:`TextWidget's <simpleline.render.widgets.TextWidget>` text.

Now the user has the header and result printed on the screen but it would be nice to give them a
hint about how to use the Divider screen. The best part of the screen for this is the
:class:`Prompt <simpleline.render.prompt.Prompt>`.
The :class:`Prompt <simpleline.render.prompt.Prompt>` class is responsible for guiding the user
by giving them a set of possible options to choose from.

We will set the message of the prompt inside of the :meth:`UIScreen.prompt` method. We also
remove the default option to continue, because it functions the same as quitting when there is
only one screen in the application.

.. code-block:: python
    :dedent: 0

        def prompt(self, args=None):
            # Change user prompt
            prompt = super().prompt()

            # Set message to the user prompt. Give a user hint how he/she may control our application.
            prompt.set_message("Pass numbers to divider in a format: 'num / num'")

            # Remove continue option from the control. There is no need for that
            # when we have only one screen.
            prompt.remove_option('c')

            return prompt

When we are able to present our content to a user, we want to have the possibility to process
user input. For this purpose there is the :meth:`UIScreen.input` method. Input from a user is
passed to this method, and the screen may process it, discard it or return it for further
processing.

If input processing is not required and the screen should only be used for displaying
information to a user, then the :attr:`UIScreen.input_required` property should be set to `False`.
However, in this case you need to :meth:`close <UIScreen.close>`, :meth:`redraw <UIScreen.redraw>`
or :ref:`push <screen_handling_label>` a new screen manually. This can be done, for example, in the
:meth:`UIScreen.show_all` method.

.. code-block:: python
    :dedent: 0

        def input(self, args, key):
            """Process input from user and catch numbers with '/' symbol."""

            # Test if user passed valid input for divider.
            # This will basically take number + number and nothing else and only positive numbers.
            groups = re.match(r'(\d+) *\/ *(\d+)$', key)
            if groups:
                num1 = int(groups[1])
                num2 = int(groups[2])

                # Dividing by zero is not valid so we won't accept this input from the user. New
                # input is then required from the user.
                if num2 == 0:
                    return InputState.DISCARDED

                self._message = int(num1 / num2)

                # Because this input is processed we need to show this screen (show the result)
                # again by returning PROCESSED_AND_REDRAW.
                # This will call the refresh method so our new result will be processed inside
                # of the refresh() method.
                return InputState.PROCESSED_AND_REDRAW
            else:
                # Not input for our screen, try other default inputs. This will result in the
                # same state as DISCARDED when no default option is used.
                return key


.. py:currentmodule:: simpleline

Our screen is finished. Next, we need to use it in our application. To run an application the
:class:`App` static class must be used.

This class will initialize an event loop and the scheduler by the :meth:`App.initialize` method.
When the application is initialized, we need to pass our screen to the screen stack (you can
pass multiple screens but we have only one here). To pass a screen to the screen stack we will use
:class:`ScreenHandler <simpleline.render.screen_handler.ScreenHandler>`. For further explanation
on screen scheduling, refer to the :ref:`screen_handling_label` section.

.. code-block:: python
    :dedent: 0

    if __name__ == "__main__":
        # Initialize application (create scheduler and event loop).
        App.initialize()

        # Create our screen.
        screen = DividerScreen()

        # Schedule screen to the screen scheduler.
        # This can be called only after App.initialize().
        ScreenHandler.schedule_screen(screen)

        # Run the application. You must have some screen scheduled
        # otherwise it will end in an infinite loop.
        App.run()

Well done! You have your first application in Simpleline.

Further reading
---------------

I would recommend everyone who wants to use Simpleline to look at the
`examples <https://github.com/rhinstaller/python-simpleline/tree/master/examples>`_ which is one
of the best sources of information. Another place to look is the :ref:`public_api_label`
documentation section.
