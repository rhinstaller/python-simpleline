#
# iutil.py - generic install utility functions
#
# Copyright (C) 1999-2014
# Red Hat, Inc.  All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


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
    elif isinstance(str_or_bytes, str):
        return str_or_bytes
    elif isinstance(str_or_bytes, bytes):
        return str_or_bytes.decode(sys.getdefaultencoding())
    else:
        raise ValueError("str_or_bytes must be of type 'str' or 'bytes', not '%s'" % type(str_or_bytes))


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

