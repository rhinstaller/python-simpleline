#!/bin/bash

if [ -z $PYTHON ]; then
    PYTHON=python3
fi

SCRIPT_DIR=$(dirname $0)

$PYTHON -m unittest discover -v -s $SCRIPT_DIR/../ -p '*_test.py'
