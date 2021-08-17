.. _containers_label:

Containers
==========

Containers are structures to hold widgets and handle automatic positioning. Containers are
essentially widgets containing other widgets. Below is a collection of default containers which
can position :ref:`widgets <widgets_label>`, but they can do more (e.g. handle user input).
Recursive composition of containers is supported.

Customized containers can also be created. See the :ref:`creating_a_custom_container_label`
section.

Container classes
-----------------

.. automodule:: simpleline.render.containers
    :members:
    :inherited-members:
    :show-inheritance:

.. _creating_a_custom_container_label:

Creating a custom container
---------------------------

If an existing container is missing a required feature, a new, customized container can be
created based on the :class:`Container` class. Container creation is essentially the same as
:ref:`custom widget creation <create_custom_widget_label>` because containers are based on widgets.
The main difference is that containers are working with widgets added by a developer when using
the container. As an example, every :class:`UIScreen <simpleline.render.screen.UIScreen>` has a
:class:`WindowContainer`, and this is used as the main rendering point.

To create a customized container, the :meth:`Container.render` method should be overridden and
the positioning of widgets and containers should be done here. It can even enhance these widgets,
for example, by adding numbering (this is done in :class:`ListRowContainer` or
:class:`ListColumnContainer`). The :meth:`Container.render` method should call the
:meth:`Container.draw` method. The :meth:`Container.draw` method should be called for every
widget placed. For a better understanding please refer to the existing implementation.

Base container class
--------------------

.. autoclass:: Container
    :members:
    :inherited-members:
    :show-inheritance:
