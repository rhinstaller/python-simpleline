#!/usr/bin/python3
#
# This file is part of Simpleline Text UI library.
#
# Copyright (C) 2020  Red Hat, Inc.
#
# Simpleline is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Simpleline is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Simpleline.  If not, see <https://www.gnu.org/licenses/>.
#

from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(name='simpleline',
      version='1.8.3',
      author='Jiri Konecny',
      author_email='jkonecny@redhat.com',
      description='Python text UI framework',
      long_description=long_description,
      long_description_content_type="text/markdown",
      keywords='ui text library glib',
      url='https://github.com/rhinstaller/python-simpleline',
      packages=find_packages(include=['simpleline', 'simpleline.*']),
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "Topic :: Software Development :: User Interfaces",
          "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
          "Programming Language :: Python :: 3",
      ],
      python_requires='>=3.4')
