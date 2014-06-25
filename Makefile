include $(B_BASE)/common.mk
include $(B_BASE)/rpmbuild.mk

VERSION := 1.0
$(eval $(shell $(call git_cset_number,xenserver-status-report)))
RELEASE := $(CSET_NUMBER)

SPEC := $(RPM_SPECSDIR)/xenserver-status-report.spec
SRPM := $(RPM_SRPMSDIR)/xenserver-status-report-$(VERSION)-$(RELEASE).src.rpm

build: $(SPEC) $(MY_SOURCES)/MANIFEST
	cp xen-bugtool help2man $(RPM_SOURCESDIR)/
	$(RPMBUILD) -ba $(SPEC)

$(SPEC): xenserver-status-report.spec.in $(RPM_DIRECTORIES) Makefile
	sed -e 's/@XS_VERSION@/$(VERSION)/; s/@XS_RELEASE@/$(RELEASE)/' < $< > $@.tmp
	mv -f $@.tmp $@

$(MY_SOURCES)/MANIFEST: $(MY_SOURCES)/.dirstamp
	echo "$(COMPONENT) gpl file $(SRPM)" > $@.tmp
	mv -f $@.tmp $@

