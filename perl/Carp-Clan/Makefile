# AWARE Perl Module Makefile

THING=perl-Carp-Clan
SRC=src/*
TOPDIR=/tmp/make_$(THING)
#ARCH=`uname -i`
ARCH=noarch

define MAKE_TARBALL
	mkdir /tmp/$(THING)-$(VERSION)/
	cp -r $(SRC) /tmp/$(THING)-$(VERSION)/
	find /tmp/$(THING)-$(VERSION)/ -type d -name .svn | xargs rm -rf
	find /tmp/$(THING)-$(VERSION)/ -type d -name CVS | xargs rm -rf
	tar -czf $(THING)-$(VERSION).tar.gz --directory /tmp $(THING)-$(VERSION)
	rm -rf /tmp/$(THING)-$(VERSION)
endef

# Extract the version number from the .spec file
VERSION := $(filter-out Version:,$(shell grep "^Version:" "rpm/$(THING).spec"))

default:
	@echo "VERSION=$(VERSION)"

$(TOPDIR):
	mkdir -p $(TOPDIR)/BUILD $(TOPDIR)/RPMS $(TOPDIR)/SOURCES $(TOPDIR)/SPECS $(TOPDIR)/SRPMS

dist:
	$(MAKE_TARBALL)

$(THING)-$(VERSION).tgz:
	$(MAKE_TARBALL)

rpm: $(TOPDIR) dist
	cp *.tar.gz $(TOPDIR)/SOURCES
	cp rpm/$(THING).spec $(TOPDIR)/SPECS
	rpmbuild -ba --define="_topdir $(TOPDIR)" $(TOPDIR)/SPECS/$(THING).spec
	cp $(TOPDIR)/SRPMS/$(THING)-$(VERSION)*.rpm ./rpm
	cp $(TOPDIR)/RPMS/$(ARCH)/$(THING)*$(VERSION)*.rpm ./rpm
	rm -rf $(TOPDIR)

clean:
	rm -rf rpm/*.rpm *.tar.gz $(TOPDIR)

.PHONY: default rpm clean dist

