#Global variables, can be overriden (eg. "make install BINDIR=/bin")
BINDIR?=/usr/bin
ZSHSITE?=/usr/share/zsh/site-functions

binaries=progs/hbshelper progs/Hierophantize progs/hbs progs/hbsinst \
progs/hbsremove progs/hieroq
hbsconf=conf/
zshcompletion=completion/_hbs

progs/hbshelper: hbshelper.c
	gcc -Wall $(CFLAGS) $(LDFLAGS) hbshelper.c -o progs/hbshelper

clean:
	rm progs/hbshelper

install: progs/hbshelper
	install -d $(DESTDIR)$(BINDIR)/
	install -d $(DESTDIR)/etc/hbs/
	install -d $(DESTDIR)/var/lib/hbs/
	install -d -m 1777 $(DESTDIR)/var/tmp/hbs/
	install -m 0755 $(binaries) $(DESTDIR)$(BINDIR)/
	install -m 0644 $(hbsconf)/* $(DESTDIR)/etc/hbs/
	[ ! -z $(DESTDIR) ]||[ -d $(ZSHSITE) ] && \
	install -D -m 0644 $(zshcompletion) $(DESTDIR)$(ZSHSITE)/_hbs
#	which update-mime-database >/dev/null 2>/dev/null &&
#	install -D hbs.xml $(DESTDIR)$(MIME)/packages/hbs.xml &&
#	update-mime-database $(DESTDIR)$(MIME)

