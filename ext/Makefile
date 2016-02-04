include $(B_BASE)/common.mk
include $(B_BASE)/rpmbuild.mk

VERSION := 1.0
$(eval $(shell $(call git_cset_number,xenserver-status-report)))
RELEASE := $(CSET_NUMBER)

SPEC := $(RPM_SPECSDIR)/bugtool-conn-tests.spec
SRPM := $(RPM_SRPMSDIR)/bugtool-conn-tests-$(VERSION)-$(RELEASE).src.rpm

build: $(SPEC) $(MY_SOURCES)/MANIFEST
	tar -czvf $(RPM_SOURCESDIR)/bugtool-conn-tests-$(VERSION).tar.gz bugtool-conn-tests
	$(RPMBUILD) -ba $(SPEC)

$(SPEC): bugtool-conn-tests.spec.in $(RPM_DIRECTORIES) Makefile
	sed -e 's/@XS_VERSION@/$(VERSION)/; s/@XS_RELEASE@/$(RELEASE)/' < $< > $@.tmp
	mv -f $@.tmp $@

$(MY_SOURCES)/MANIFEST: $(MY_SOURCES)/.dirstamp
	echo "$(COMPONENT) $(call rpm_license,$(SRPM)) file $(SRPM)" >$@
