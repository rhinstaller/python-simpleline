# Logging functions and methods used by Simpleline.
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
# Author(s): Jiri Konecny <jkonecny@redhat.com>
#


import logging


SIMPLELINE_LOGGER = "simpleline"


def setup_logging():
    """Set proper logging for a library"""
    log = get_simpleline_logger()
    null_hd = logging.NullHandler()
    log.addHandler(null_hd)


def get_simpleline_logger():
    """Return logging instance that can be used in the application."""
    return logging.getLogger(SIMPLELINE_LOGGER)
