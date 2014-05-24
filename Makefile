VERSION=0.2
DEBVERSION=0.2
SOURCES=$(shell find code -name '*.py')
TESTDATA=$(shell find code -name '*.svg')

all: dist/svgplease_${VERSION}-${DEBVERSION}_all.deb

dist/svgplease_${VERSION}-${DEBVERSION}_all.deb: ${SOURCES} ${TESTDATA}
	mkdir -p deb/DEBIAN
	mkdir -p deb/usr/share/svgplease
	mkdir -p deb/usr/share/doc/svgplease
	mkdir -p deb/usr/share/man/man1
	mkdir -p deb/usr/bin
	mkdir -p deb/usr/share/fish/completions
	mkdir -p dist
	cp changelog deb/usr/share/doc/svgplease
	cp copyright deb/usr/share/doc/svgplease
	gzip --best -f deb/usr/share/doc/svgplease/changelog
	cp --preserve debian/* -R deb/DEBIAN
	cp --preserve code -R deb/usr/share/svgplease/code
	cp --preserve svgplease deb/usr/share/svgplease/
	cp --preserve svgplease.fish deb/usr/share/fish/completions
	rm -rf $$(find deb -name '__pycache__' -or -name 'dist')
	rm -rf $$(find deb -name '*.swp' -or -name '*.pyc')
	rst2man doc/man.rst > deb/usr/share/man/man1/svgplease.1
	gzip --best -f deb/usr/share/man/man1/svgplease.1
	ln -s ../share/svgplease/svgplease deb/usr/bin/svgplease
	./generateMd5Sums.bash
	bash -c 'sed --in-place "s/Installed-Size:.*/Installed-Size: $$(du deb/usr -s | cut -f 1)/" deb/DEBIAN/control'
	chmod g-w deb -R
	fakeroot dpkg-deb -D --build deb dist/svgplease_${VERSION}-${DEBVERSION}_all.deb
	dpkg-sig --sign builder dist/svgplease_${VERSION}-${DEBVERSION}_all.deb

clean:
	rm dist deb -rf
