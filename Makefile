INSTALL_PROG = install -m u=rwx,go=rx -g wheel -p
INSTALL_DATA = install -m u=rw,go=r -g wheel -p

all:
	@

install:
	$(INSTALL_PROG) xen-bugtool $(STAGING)/usr/sbin
	$(INSTALL_DATA) sexp.py $(STAGING)/usr/lib/python
