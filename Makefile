INSTALL_PROG = install    -m u=rwx,go=rx -g wheel -p
INSTALL_DATA = install    -m u=rw,go=r   -g wheel -p
INSTALL_DIR  = install -d -m u=rwx,go=rx  g wheel -p

all:
	@

install:
	$(INSTALL_PROG) xen-bugtool $(STAGING)/usr/sbin
	$(INSTALL_DIR) $(STAGING)/usr/lib/python
	$(INSTALL_DATA) sexp.py $(STAGING)/usr/lib/python
