# Class for the Anaconda TUI prompt.
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
# Author(s):  Vendula Poncova <vponcova@redhat.com>
#

from simpleline.utils.i18n import C_, N_, _

import logging
log = logging.getLogger("simpleline")


class Prompt(object):
    """Class to create a prompt message with options."""
    # Default message of the prompt
    DEFAULT_MESSAGE = N_("Please make a selection from the above")

    # String to use in a prompt when we want users to press the key ENTER.
    ENTER = N_("ENTER")

    # TRANSLATORS: 'q' to quit
    QUIT = C_('TUI|Spoke Navigation', 'q')
    QUIT_DESCRIPTION = N_("to quit")

    # TRANSLATORS:'c' to continue
    CONTINUE = C_('TUI|Spoke Navigation', 'c')
    CONTINUE_DESCRIPTION = N_("to continue")

    # TRANSLATORS:'r' to refresh
    REFRESH = C_('TUI|Spoke Navigation', 'r')
    REFRESH_DESCRIPTION = N_("to refresh")

    # TRANSLATORS:'h' to help
    HELP = C_('TUI|Spoke Navigation', 'h')
    HELP_DESCRIPTION = N_("to help")

    def __init__(self, message=DEFAULT_MESSAGE):
        """
        :param message: the message of the prompt
        :type message: str|None
        """
        self.message = message
        self.options = dict()

    def set_message(self, message):
        """Set the prompt message.

        :param message: the message of the prompt
        :type message: str|None
        """
        self.message = message

    def add_option(self, key, description):
        """Add an option to the prompt.
        Causes a warning if the option already exists.

        :param key: the key for choosing the option
        :type key: str

        :param description: the description of the option
        :type description: str
        """
        if key in self.options:
            log.warning("The option '%s' does already exist in '%s'.", key, self)

        self.options[key] = description

    def update_option(self, key, description):
        """Update an option in the prompt.
        Causes a warning if the option does not exist.

        :param key: the key for choosing the option
        :type key: str

        :param description: the description of the option
        :type description: str
        """
        if key not in self.options:
            log.warning("The option '%s' does not exist in '%s'.", key, self)

        self.options[key] = description

    def add_refresh_option(self, description=REFRESH_DESCRIPTION):
        """Add the option to refresh."""
        if Prompt.REFRESH in self.options:
            self.update_option(Prompt.REFRESH, description)
        else:
            self.add_option(Prompt.REFRESH, description)

    def add_continue_option(self, description=CONTINUE_DESCRIPTION):
        """Add the option to continue."""
        if Prompt.CONTINUE in self.options:
            self.update_option(Prompt.CONTINUE, description)
        else:
            self.add_option(Prompt.CONTINUE, description)

    def add_quit_option(self, description=QUIT_DESCRIPTION):
        """Add the option to quit."""
        if Prompt.QUIT in self.options:
            self.update_option(Prompt.QUIT, description)
        else:
            self.add_option(Prompt.QUIT, description)

    def add_help_option(self, description=HELP_DESCRIPTION):
        """Add the option to help."""
        if Prompt.HELP in self.options:
            self.update_option(Prompt.HELP, description)
        else:
            self.add_option(Prompt.HELP, description)

    def remove_option(self, key):
        """Remove an option with the given key.

        :param key: the key of the option
        :type key: str

        :return: the removed option
        :rtype: str|None
        """
        return self.options.pop(key, None)

    def __str__(self):
        """Return the string representation of the prompt."""
        if not self.message and not self.options:
            return ""

        parts = []

        if self.message:
            parts.append(_(self.message))

        if self.options:
            opt_list = ["'%s' %s" % (key, _(self.options[key]))
                        for key in sorted(self.options.keys())]
            opt_str = "[%s]" % ", ".join(opt_list)
            parts.append(opt_str)

        return " ".join(parts) + ": "
