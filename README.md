Python Simpleline
=================

This is a text UI framework originally which was a part of the
[Anaconda](https://github.com/rhinstaller/anaconda) installer project.

This UI is simple and easy to use. It is designed to be used with line-based
machines and tools (e.g. serial console) so that every new line is appended
to the bottom of the screen. Printed lines are never rewritten!

How to
======

[Link](python-simpleline.readthedocs.io) to the documentation.

Another way to learn how to use this library is to view the examples directory.
Examples can be run without installing Simpleline to the system. You can test
them by running the script `run_example.sh`.

1. `cd examples`
2. `./run_example.sh example_folder_name`

For example:
`./run_example.sh basic`

Dependencies
============

This is a Python3-only project. This code should not be difficult to migrate to
Python2. However, there is no need from the community, so it is only compatible
with Python3 at the moment.
No special libraries are required to use this library. If you want to use glib
event loop instead of the original one you need to install glib and Python3
gobject introspection.

If you want to run tests (`make ci`), you need to install
[Pocketlint](https://github.com/rhinstaller/pocketlint) and glib with gobject
introspection for Python3.

Note
====

Thanks to Martin Sivák for the original Anaconda project. It was really nice
starting place for the new Simpleline's form.
