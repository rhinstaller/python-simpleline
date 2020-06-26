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

PKGNAME=simpleline
SPECNAME=python-$(PKGNAME)
VERSION=$(shell awk '/Version:/ { print $$2 }' $(SPECNAME).spec)
RELEASE=$(shell awk '/Release:/ { print $$2 }' $(SPECNAME).spec | sed -e 's|%.*$$||g')
TAG=$(PKGNAME)-$(VERSION)

PYTHON=python3

# Arguments used for setup.py call for creating archive
BUILD_ARGS ?= sdist bdist_wheel

# LOCALIZATION SETTINGS
L10N_REPOSITORY ?= https://github.com/rhinstaller/python-simpleline-l10n.git
L10N_REPOSITORY_RW ?= git@github.com:rhinstaller/python-simpleline-l10n.git

# Branch used in localization repository. This should be master all the time.
GIT_L10N_BRANCH ?= master
# Directory in localization repository specific for this branch.
L10N_DIR ?= master

default: all

.PHONY: all
all:
	$(MAKE) -C po

.PHONY: clean
clean:
	-rm -rf *.tar.gz simpleline/*.pyc tests/*.pyc ChangeLog dist build simpleline.egg-info
	$(MAKE) -C po clean
	$(PYTHON) setup.py -q clean --all

.PHONY: test
test:
	@echo "*** Running unittests ***"
	PYTHONPATH=. $(PYTHON) -m unittest discover -v -s tests/ -p '*_test.py'

.PHONY: check
check:
	@echo "*** Running pocketlint ***"
	PYTHONPATH=. tests/pylint/runpylint.py

.PHONY: install
install:
	$(PYTHON) setup.py install --root=$(DESTDIR)
	$(MAKE) -C po install

.PHONY: ChangeLog
ChangeLog:
	(GIT_DIR=.git git log > .changelog.tmp && mv .changelog.tmp ChangeLog; rm -f .changelog.tmp) || (touch ChangeLog; echo 'git directory not found: installing possibly empty changelog.' >&2)

.PHONY: tag
tag:
	git tag -a -m "Tag as $(TAG)" -f $(TAG)
	@echo "Tagged as $(TAG)"

.PHONY: release
release: tag archive

.PHONY: archive
archive: po-pull ChangeLog
	$(PYTHON) setup.py $(BUILD_ARGS)
	@echo "The archive is in dist/$(PKGNAME)-$(VERSION).tar.gz"

.PHONY: rpmlog
rpmlog:
	@git log --no-merges --pretty="format:- %s (%ae)" $(TAG).. |sed -e 's/@.*)/)/'
	@echo

.PHONY: potfile
potfile:
	$(MAKE) -C po potfile

.PHONY: po-pull
po-pull:
	TEMP_DIR=$$(mktemp --tmpdir -d $(SPECNAME)-localization-XXXXXXXXXX) && \
	git clone --depth 1 -b $(GIT_L10N_BRANCH) -- $(L10N_REPOSITORY) $$TEMP_DIR && \
	cp $$TEMP_DIR/$(L10N_DIR)/*.po ./po/ && \
	rm -rf $$TEMP_DIR

.PHONY: po-push
po-push: potfile
# This algorithm will make these steps:
# - clone localization repository
# - copy pot file to this repository
# - check if pot file is changed (ignore the POT-Creation-Date otherwise it's always changed)
# - if not changed:
#   - remove cloned repository
# - if changed:
#   - add pot file
#   - commit pot file
#   - tell user to verify this file and push to the remote from the temp dir
	TEMP_DIR=$$(mktemp --tmpdir -d $(SPECNAME)-localization-XXXXXXXXXX) || exit 1 ; \
	git clone --depth 1 -b $(GIT_L10N_BRANCH) -- $(L10N_REPOSITORY_RW) $$TEMP_DIR || exit 2 ; \
	cp ./po/$(SPECNAME).pot $$TEMP_DIR/$(L10N_DIR)/ || exit 3 ; \
	pushd $$TEMP_DIR/$(L10N_DIR) ; \
	git difftool --trust-exit-code -y -x "diff -u -I '^\"POT-Creation-Date: .*$$'" HEAD ./$(SPECNAME).pot &>/dev/null ; \
	if [ $$? -eq 0  ] ; then \
		popd ; \
		echo "Pot file is up to date" ; \
		rm -rf $$TEMP_DIR ; \
	else \
		git add ./$(SPECNAME).pot && \
		git commit -m "Update $(SPECNAME).pot" && \
		popd && \
		echo "Pot file updated for the localization repository $(L10N_REPOSITORY)" && \
		echo "Please confirm changes and push:" && \
		echo "$$TEMP_DIR" ; \
	fi ;

.PHONY: bumpver
bumpver:
	@NEWSUBVER=$$((`echo $(VERSION) |cut -d . -f 2` + 1)) ; \
	NEWVERSION=`echo $(VERSION).$$NEWSUBVER |cut -d . -f 1,3` ; \
	DATELINE="* `LC_ALL=C.UTF-8 date "+%a %b %d %Y"` `git config user.name` <`git config user.email`> - $$NEWVERSION-1"  ; \
	cl=`grep -n %changelog $(SPECNAME).spec |cut -d : -f 1` ; \
	tail --lines=+$$(($$cl + 1)) $(SPECNAME).spec > speclog ; \
	(head -n $$cl $(SPECNAME).spec ; echo "$$DATELINE" ; make --quiet rpmlog 2>/dev/null ; echo ""; cat speclog) > $(SPECNAME).spec.new ; \
	mv $(SPECNAME).spec.new $(SPECNAME).spec ; rm -f speclog ; \
	sed -i "s/Version: $(VERSION)/Version: $$NEWVERSION/" $(SPECNAME).spec ; \
	sed -i "s/version='$(VERSION)'/version='$$NEWVERSION'/" setup.py

.PHONY: ci
ci: check test
