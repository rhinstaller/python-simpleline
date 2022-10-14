# Translation functions we use all over the place
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

__all__ = ["_", "N_", "P_", "C_", "CN_", "CP_"]

import gettext

# pylint: disable=unnecessary-lambda-assignment
N_ = lambda x: x
_ = lambda x: gettext.translation("python-simpleline", fallback=True).gettext(x) if x != "" else ""
P_ = lambda x, y, z: gettext.translation("python-simpleline", fallback=True).ngettext(x, y, z)

# This is equivalent to "pgettext" in GNU gettext. The pgettext functions
# are not exported by Python, but all they really do is a stick a EOT
# character between msgctxt and msgid and check that msgctxt isn't part
# of the return value.


def C_(msgctxt, msgid):
    ctxid = "%s\x04%s" % (msgctxt, msgid)
    translation = _(ctxid)

    # If there is no translation for msgctxt<EOT>msgid, return only msgid
    if translation == ctxid:
        return msgid

    return translation

# Mark as translatable with context
CN_ = lambda c, x: x

# npgettext; i.e., gettext with plural form and context


def CP_(msgctxt, msgid, msgid_plural, n):
    ctxid = "%s\x04%s" % (msgctxt, msgid)
    translation = P_(ctxid, msgid_plural, n)

    # If the returned value is msgctxt<EOT>msgid, ngettext was trying to
    # fallback to msgid. We don't add msgctxt to msgid_plural, so any other
    # return value is correct.
    if translation == ctxid:
        return msgid

    return translation
