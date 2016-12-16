#!/usr/bin/python3

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
