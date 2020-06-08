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

from distutils.core import setup

setup(name='simpleline', version='1.6',
      description='Python text UI framework',
      author='Jiri Konecny', author_email='jkonecny@redhat.com',
      url='http://git.fedoraproject.org/git/?p=python-simpleline.git',
      packages=['simpleline', 'simpleline.render', 'simpleline.render.screen',
                'simpleline.event_loop', 'simpleline.utils', 'simpleline.input'])
