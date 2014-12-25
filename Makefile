# -- AWARE Makefile
TARGET=aware

# Determine the Architecture (32-bit vs 64-bit)
ARCH=`uname -i`

# Create a working/build directory
TOPDIR  := $(shell mktemp -d /tmp/make_$(TARGET)_XXXXXX )

# Extract the version number from the .spec file
VERSION := $(shell grep ^VERSION= version.txt | sed 's/VERSION=//g')
SVNREPO := $(shell SVN_SSH='ssh -q' svn info | awk '{if ( and ( ($$1 == "Repository" ), ($$2 == "Root:") ) ) { print $$3}}')
SVNURL  := $(shell SVN_SSH='ssh -q' svn info `pwd` | awk '{if ($$1 == "URL:") {print $$2}}' )
SVNREV  := $(shell SVN_SSH='ssh -q' svn info $(SVNURL) | awk '{if (and ( ($$1 == "Last"), ($$3 == "Rev:") ) ) {print $$4}}' | bc )

define MAKE_TARBALL
	mkdir /tmp/$(TARGET)-$(VERSION)/
	cp -r bin cfg doc logs pids schema web /tmp/$(TARGET)-$(VERSION)/
	find /tmp/$(TARGET)-$(VERSION)/ -type d -name .svn | xargs rm -rf
	find /tmp/$(TARGET)-$(VERSION)/ -type d -name CVS | xargs rm -rf
	tar -czf $(TARGET)-$(VERSION).tar.gz --directory /tmp $(TARGET)-$(VERSION)
	rm -rf /tmp/$(TARGET)-$(VERSION)
endef

default:
	@echo "VERSION=$(VERSION)"
	@echo "TOPDIR=$(TOPDIR)"
	@echo "SVNREPO=$(SVNREPO)"
	@echo "SVNURL=$(SVNURL)"
	@echo "SVNREV=$(SVNREV)"

tmpdir:
	mkdir -p $(TOPDIR)/BUILD $(TOPDIR)/RPMS $(TOPDIR)/SOURCES $(TOPDIR)/SPECS $(TOPDIR)/SRPMS

dist:
	$(MAKE_TARBALL)

rpm: default tmpdir dist
	(cd perl/ZUtils-Common && make rpm && cp rpm/*.$(ARCH).rpm ../../rpm/ && cp rpm/*.src.rpm ../../srpm/)
	(cd perl/ZUtils-Aware && make rpm && cp rpm/*.$(ARCH).rpm ../../rpm/ && cp rpm/*.src.rpm ../../srpm/)
	(cd perl/GD && make rpm && cp rpm/*.$(ARCH).rpm ../../rpm/ && cp rpm/*.src.rpm ../../srpm/)
	(cd perl/XML-Writer && make rpm && cp rpm/*.noarch.rpm ../../rpm/ && cp rpm/*.src.rpm ../../srpm/)
	(cd perl/GD-Graph && make rpm && cp rpm/*.noarch.rpm ../../rpm/ && cp rpm/*.src.rpm ../../srpm/)
	(cd perl/GD-Graph3d && make rpm && cp rpm/*.noarch.rpm ../../rpm/ && cp rpm/*.src.rpm ../../srpm/)
	(cd perl/GD-TextUtil && make rpm && cp rpm/*.noarch.rpm ../../rpm/ && cp rpm/*.src.rpm ../../srpm/)
	(cd perl/Carp-Clan && make rpm && cp rpm/*.noarch.rpm ../../rpm/ && cp rpm/*.src.rpm ../../srpm/)
	(cd perl/Bit-Vector && make rpm && cp rpm/*.$(ARCH).rpm ../../rpm/ && cp rpm/*.src.rpm ../../srpm/)
	(cd perl/Date-Calc && make rpm && cp rpm/*.$(ARCH).rpm ../../rpm/ && cp rpm/*.src.rpm ../../srpm/)
	cp *.tar.gz $(TOPDIR)/SOURCES
	cp rpm/$(TARGET).spec $(TOPDIR)/SPECS/
	sed -i 's/^Version:.*/Version:\t$(VERSION)/g' $(TOPDIR)/SPECS/$(TARGET).spec
	rpmbuild -ba --define="_topdir $(TOPDIR)" $(TOPDIR)/SPECS/$(TARGET).spec
	cp $(TOPDIR)/SRPMS/$(TARGET)-$(VERSION)*.rpm ./rpm/
	cp $(TOPDIR)/RPMS/*/$(TARGET)*$(VERSION)*.rpm ./rpm/
	rm -rf $(TOPDIR)

release:
	SVN_SSH='ssh -q' svn export --revision $(SVNREV) $(SVNURL) $(TOPDIR)/$(TARGET)
	SVN_SSH='ssh -q' svn log --revision $(SVNREV):1 $(SVNURL) > $(TOPDIR)/$(TARGET)/doc/revision_history.txt
	sed -i 's/^my $$major.*/my $$major = $(VERSION);/g' $(TOPDIR)/$(TARGET)/schema/reload_mysql
	sed -i 's/^Version:.*/Version:\t$(VERSION)/g' $(TOPDIR)/$(TARGET)/rpm/$(TARGET).spec
	sed -i 's/^Release:.*/Release:\t$(SVNREV)/g' $(TOPDIR)/$(TARGET)/rpm/$(TARGET).spec
	sed -i 's%^URL:.*%URL:\t$(SVNURL)%g' $(TOPDIR)/$(TARGET)/rpm/$(TARGET).spec
	sed -i 's%^URL:.*$(SVNREPO)%URL:\t%g' $(TOPDIR)/$(TARGET)/rpm/$(TARGET).spec
	$(MAKE) -C $(TOPDIR)/$(TARGET) rpm
	mv $(TOPDIR)/$(TARGET)/rpm/*.rpm rpm/.
	rm -rf $(TOPDIR)

clean:
	rm -rf rpm/*.rpm *.tar.gz perl/*/rpm/*.rpm perl/*/*.gz srpm/*.src.rpm /tmp/make_$(TARGET)_?????? 

.PHONY: default rpm clean dist

