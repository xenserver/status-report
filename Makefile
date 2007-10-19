INSTALL_PROG = install -m u=rwx,go=rx -g wheel -p

all:
	@

install:
	$(INSTALL_PROG) xen-bugtool $(STAGING)/usr/sbin
