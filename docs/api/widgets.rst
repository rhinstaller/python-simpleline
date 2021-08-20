.. _widgets_label:

Widgets
=======

.. currentmodule:: simpleline.render.widgets

Widgets are the basic units to render items on a
:class:`screen <simpleline.render.screen.UIScreen>`. Widgets can wrap a common text
(:class:`TextWidget`) or create empty lines (:class:`SeparatorWidget`). They can also be more
complex structures (:class:`CheckboxWidget`). A new widget can also be created.
See :ref:`create_custom_widget_label`.

These widgets should be used in :ref:`containers_label`.

Widgets classes
---------------

.. automodule:: simpleline.render.widgets
    :members:
    :inherited-members:
    :show-inheritance:

.. _create_custom_widget_label:

Creating a custom widget
------------------------

To create a custom widget you should subclass the :class:`Widget` class. The most important method
for creating a customized widget is :meth:`Widget.render`. This method is responsible for
presenting a user textual information.

If the new widget is composed of other widgets the :meth:`Widget.draw` method should be
called on every widget used. The :meth:`Widget.write` method should be called if the input
is a string. These calls can be repeated multiple times. For an example please look at the
existing implementation.

Base Widget class
-----------------

.. autoclass:: Widget
    :members:
    :inherited-members:
    :show-inheritance:
