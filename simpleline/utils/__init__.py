# iutil.py - generic install utility functions
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
import string  # pylint: disable=deprecated-module
import unicodedata


def ensure_str(str_or_bytes, keep_none=True):
    """
    Returns a str instance for given string or ``None`` if requested to keep it.

    :param str_or_bytes: string to be kept or converted to str type
    :type str_or_bytes: str or bytes
    :param bool keep_none: whether to keep None as it is or raise ValueError if
                           ``None`` is passed
    :raises ValueError: if applied on an object not being of type bytes nor str
                        (nor NoneType if ``keep_none`` is ``False``)
    """
    if keep_none and str_or_bytes is None:
        return None
    if isinstance(str_or_bytes, str):
        return str_or_bytes
    if isinstance(str_or_bytes, bytes):
        return str_or_bytes.decode(sys.getdefaultencoding())

    raise ValueError(
        "str_or_bytes must be of type 'str' or 'bytes', not '%s'" % type(str_or_bytes))


# Define translations between ASCII uppercase and lowercase for
# locale-independent string conversions. The tables are 256-byte string used
# with str.translate. If str.translate is used with a unicode string,
# even if the string contains only 7-bit characters, str.translate will
# raise a UnicodeDecodeError.
_ASCIIlower_table = str.maketrans(string.ascii_uppercase, string.ascii_lowercase)
_ASCIIupper_table = str.maketrans(string.ascii_lowercase, string.ascii_uppercase)


def _toASCII(s):
    """Convert a unicode string to ASCII"""
    if isinstance(s, str):
        # Decompose the string using the NFK decomposition, which in addition
        # to the canonical decomposition replaces characters based on
        # compatibility equivalence (e.g., ROMAN NUMERAL ONE has its own code
        # point but it's really just a capital I), so that we can keep as much
        # of the ASCII part of the string as possible.
        s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode("ascii")
    elif not isinstance(s, bytes):
        s = ''
    return s


def lowerASCII(s):
    """Convert a string to lowercase using only ASCII character definitions.

    The returned string will contain only ASCII characters. This function is
    locale-independent.
    """
    # XXX: Python 3 has str.maketrans() and bytes.maketrans() so we should
    # ideally use one or the other depending on the type of 's'. But it turns
    # out we expect this function to always return string even if given bytes.
    s = ensure_str(s)
    return str.translate(_toASCII(s), _ASCIIlower_table)


def upperASCII(s):
    """Convert a string to uppercase using only ASCII character definitions.

    The returned string will contain only ASCII characters. This function is
    locale-independent.
    """
    # XXX: Python 3 has str.maketrans() and bytes.maketrans() so we should
    # ideally use one or the other depending on the type of 's'. But it turns
    # out we expect this function to always return string even if given bytes.
    s = ensure_str(s)
    return str.translate(_toASCII(s), _ASCIIupper_table)
