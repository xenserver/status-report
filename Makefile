include $(B_BASE)/common.mk
include $(B_BASE)/rpmbuild.mk

VERSION := 1.0
$(eval $(shell $(call git_cset_number,xenserver-status-report)))
RELEASE := $(CSET_NUMBER)

SPEC := $(RPM_SPECSDIR)/xenserver-status-report.spec

build: $(SPEC)
	cp xen-bugtool $(RPM_SOURCESDIR)/
	$(RPMBUILD) -ba $(SPEC)

$(SPEC): xenserver-status-report.spec.in $(RPM_DIRECTORIES) Makefile
	sed -e 's/@XS_VERSION@/$(VERSION)/; s/@XS_RELEASE@/$(RELEASE)/' < $< > $@.tmp
	mv -f $@.tmp $@

