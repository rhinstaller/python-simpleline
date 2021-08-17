.. _prompt_label:

Prompt
======

.. automodule:: simpleline.render.prompt

Class for prompting a user for input. New user options can be added by :meth:`Prompt.add_option`,
removed by :meth:`Prompt.remove_option` or updated by :meth:`Prompt.update_option`.
A message for the user can also be set by the :meth:`Prompt.set_message` method.

This class is used in the :class:`UIScreen <simpleline.render.screen.UIScreen>` class. The default
instance always handles *r* (refresh), *c* (continue) and *q* (quit) and is created in the
:meth:`UIScreen.prompt() <simpleline.render.screen.UIScreen.prompt>` method. To create your own
custom prompt please override
the :meth:`UIScreen.prompt() <simpleline.render.screen.UIScreen.prompt>` method.

Prompt class
------------

.. autoclass:: Prompt
    :members:
    :inherited-members:
