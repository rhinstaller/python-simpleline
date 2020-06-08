# Base exceptions for the Simpleline application.
#
# Base class for Simpleline Text UI framework.
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
# This can't be moved to __init__.py because of cyclic imports error.
#


class SimplelineError(Exception):
    """Base exception for all other exceptions."""


class NothingScheduledError(SimplelineError):
    """Exception when running the loop with no screens scheduled."""
