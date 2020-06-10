#!/bin/bash
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

# Script for starting examples from source code.
#
# Author(s): Jiri Konecny <jkonecny@redhat.com>
#


function print_help {
    echo "run_example.sh - easy way how to run example without installing module"
    echo ""
    echo "./run_example.sh [example]"
    echo ""
    echo "There is one required argument [example] which is name of the test."
    echo ""
}

if [[ $# -ne 1 ]]; then
    echo "Bad number of arguments" 1>&2
    print_help
    exit 1
elif [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
    print_help
    exit 0
fi

PROJECT_NAME=${1%%/}

pushd $(pwd)
cd $(dirname $0)/
PYTHONPATH="..:." python3 ./$PROJECT_NAME/$PROJECT_NAME.py
popd

