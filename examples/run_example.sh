#!/bin/bash
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

