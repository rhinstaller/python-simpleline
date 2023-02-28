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

# Makefile for the PO files (translation) catalog
#
# $Id$

TOP	 = ../..

# Variables used in xgettext arguments
COPYRIGHT_HOLDER = Red Hat, Inc.
MSGID_BUGS_ADDRESS = anaconda-devel@lists.fedoraproject.org

# What is this package?
NLSPACKAGE	= python-simpleline
POTFILE		= $(NLSPACKAGE).pot
INSTALL		= /usr/bin/install -c
INSTALL_DATA	= $(INSTALL) -m 644
INSTALL_DIR	= /usr/bin/install -d

# destination directory
INSTALL_NLS_DIR = $(RPM_BUILD_ROOT)/usr/share/locale

# PO catalog handling
MSGMERGE	= msgmerge -v
XGETTEXT	= xgettext \
	--default-domain=$(NLSPACKAGE) \
	--add-comments \
	--sort-output \
	--package-name=$(PKGNAME) \
	--package-version=$(VERSION) \
	--copyright-holder="$(COPYRIGHT_HOLDER)" \
	--msgid-bugs-address="$(MSGID_BUGS_ADDRESS)"

MSGFMT		= msgfmt --statistics --verbose

# What do we need to do
POFILES		= $(wildcard *.po)
MOFILES		= $(patsubst %.po,%.mo,$(POFILES))
PYSRC		= $(wildcard ../simpleline/*.py) $(wildcard ../simpleline/**/*.py)

all::  update-po $(MOFILES)

potfile: $(PYSRC)
	$(XGETTEXT) -L Python --keyword=_ --keyword=N_ $(PYSRC)
	@if cmp -s $(NLSPACKAGE).po $(POTFILE); then \
	    rm -f $(NLSPACKAGE).po; \
	else \
	    mv -f $(NLSPACKAGE).po $(POTFILE); \
	fi; \

update-po: Makefile potfile refresh-po

refresh-po: Makefile
	for cat in $(POFILES); do \
		lang=`basename $$cat .po`; \
		if $(MSGMERGE) $$lang.po $(POTFILE) > $$lang.pot ; then \
			mv -f $$lang.pot $$lang.po ; \
			echo "$(MSGMERGE) of $$lang succeeded" ; \
		else \
			echo "$(MSGMERGE) of $$lang failed" ; \
			rm -f $$lang.pot ; \
		fi \
	done

clean:
	@rm -fv *mo *~ .depend

install: $(MOFILES)
	@for n in $(MOFILES); do \
	    l=`basename $$n .mo`; \
	    $(INSTALL_DIR) $(INSTALL_NLS_DIR)/$$l/LC_MESSAGES; \
	    $(INSTALL_DATA) --verbose $$n $(INSTALL_NLS_DIR)/$$l/LC_MESSAGES/$(NLSPACKAGE).mo; \
	done

%.mo: %.po
	$(MSGFMT) -o $@ $<

.PHONY: missing depend


