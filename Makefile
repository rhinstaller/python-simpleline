PKGNAME=simpleline
SPECNAME=python-$(PKGNAME)
VERSION=$(shell awk '/Version:/ { print $$2 }' $(SPECNAME).spec)
RELEASE=$(shell awk '/Release:/ { print $$2 }' $(SPECNAME).spec | sed -e 's|%.*$$||g')
TAG=$(PKGNAME)-$(VERSION)

PREFIX=/usr

PYTHON=python3

# LOCALIZATION SETTINGS
L10N_REPOSITORY ?= https://github.com/rhinstaller/python-simpleline-l10n.git

# Branch used in localization repository. This should be master all the time.
GIT_L10N_BRANCH ?= master
# Directory in localization repository specific for this branch.
L10N_DIR ?= master

ZANATA_PULL_ARGS = --transdir po/
ZANATA_PUSH_ARGS = --srcdir po/ --push-type source --force

default: all

all:
	$(MAKE) -C po

clean:
	-rm *.tar.gz simpleline/*.pyc tests/*.pyc ChangeLog
	$(MAKE) -C po clean
	$(PYTHON) setup.py -q clean --all

test:
	@echo "*** Running unittests ***"
	PYTHONPATH=. $(PYTHON) -m unittest discover -v -s tests/ -p '*_test.py'

check:
	@echo "*** Running pocketlint ***"
	PYTHONPATH=. tests/pylint/runpylint.py

install:
	$(PYTHON) setup.py install --root=$(DESTDIR)
	$(MAKE) -C po install

ChangeLog:
	(GIT_DIR=.git git log > .changelog.tmp && mv .changelog.tmp ChangeLog; rm -f .changelog.tmp) || (touch ChangeLog; echo 'git directory not found: installing possibly empty changelog.' >&2)

tag:
	git tag -a -m "Tag as $(TAG)" -f $(TAG)
	@echo "Tagged as $(TAG)"

release: tag archive

archive: po-pull
	@rm -f ChangeLog
	@make ChangeLog
	git archive --format=tar --prefix=$(PKGNAME)-$(VERSION)/ $(TAG) > $(PKGNAME)-$(VERSION).tar
	mkdir $(PKGNAME)-$(VERSION)
	cp -r po $(PKGNAME)-$(VERSION)
	cp ChangeLog $(PKGNAME)-$(VERSION)/
	tar -rf $(PKGNAME)-$(VERSION).tar $(PKGNAME)-$(VERSION)
	gzip -9 $(PKGNAME)-$(VERSION).tar
	rm -rf $(PKGNAME)-$(VERSION)
	git checkout -- po/python-$(PKGNAME).pot
	@echo "The archive name is $(PKGNAME)-$(VERSION).tar.gz"

local: po-pull
	@rm -f ChangeLog
	@make ChangeLog
	rm -rf $(PKGNAME)-$(VERSION).tar.gz
	rm -rf /tmp/$(PKGNAME)-$(VERSION) /tmp/$(PKGNAME)
	dir=$$PWD; cp -a $$dir /tmp/$(PKGNAME)-$(VERSION)
	cd /tmp/$(PKGNAME)-$(VERSION) ; $(PYTHON) setup.py -q sdist
	cp /tmp/$(PKGNAME)-$(VERSION)/dist/$(PKGNAME)-$(VERSION).tar.gz .
	rm -rf /tmp/$(PKGNAME)-$(VERSION)
	@echo "The archive name is $(PKGNAME)-$(VERSION).tar.gz"

rpmlog:
	@git log --no-merges --pretty="format:- %s (%ae)" $(TAG).. |sed -e 's/@.*)/)/'
	@echo

potfile:
	$(MAKE) -C po potfile

po-pull:
	TEMP_DIR=$$(mktemp --tmpdir -d $(SPECNAME)-localization-XXXXXXXXXX) && \
	git clone --depth 1 -b $(GIT_L10N_BRANCH) -- $(L10N_REPOSITORY) $$TEMP_DIR && \
	cp $$TEMP_DIR/$(L10N_DIR)/*.po ./po/ && \
	rm -rf $$TEMP_DIR

po-push: potfile
	zanata push $(ZANATA_PUSH_ARGS) || ( echo "zanata push failed"; exit 1 )

bumpver: po-push
	@NEWSUBVER=$$((`echo $(VERSION) |cut -d . -f 2` + 1)) ; \
	NEWVERSION=`echo $(VERSION).$$NEWSUBVER |cut -d . -f 1,3` ; \
	DATELINE="* `LANG=c date "+%a %b %d %Y"` `git config user.name` <`git config user.email`> - $$NEWVERSION-1"  ; \
	cl=`grep -n %changelog $(SPECNAME).spec |cut -d : -f 1` ; \
	tail --lines=+$$(($$cl + 1)) $(SPECNAME).spec > speclog ; \
	(head -n $$cl $(SPECNAME).spec ; echo "$$DATELINE" ; make --quiet rpmlog 2>/dev/null ; echo ""; cat speclog) > $(SPECNAME).spec.new ; \
	mv $(SPECNAME).spec.new $(SPECNAME).spec ; rm -f speclog ; \
	sed -i "s/Version: $(VERSION)/Version: $$NEWVERSION/" $(SPECNAME).spec ; \
	sed -i "s/version='$(VERSION)'/version='$$NEWVERSION'/" setup.py

ci: check test

.PHONY: clean install tag archive local
