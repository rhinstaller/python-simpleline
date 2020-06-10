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

import sys

from pocketlint import PocketLintConfig, PocketLinter

class SimplelineLintConfig(PocketLintConfig):
    def __init__(self):
        PocketLintConfig.__init__(self)


if __name__ == "__main__":
    conf = SimplelineLintConfig()
    linter = PocketLinter(conf)
    rc = linter.run()
    sys.exit(rc)
