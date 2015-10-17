VERSION=$(shell head debian/changelog -n 1 | sed 's/.*(//' | sed 's/).*//')
SOURCES=$(shell find code -name '*.py')
TESTDATA=$(shell find code -name '*.svg')
DOC=$(shell find doc)
DEBIAN=$(shell find debian)
DEB_DIR=deb/svgplease-${VERSION}

all: deb/svgplease_${VERSION}_all.deb

doc/html/manual.html:doc/man.rst doc/html/html4css1.css doc/html/man.css
	rst2html doc/man.rst --stylesheet=doc/html/html4css1.css,doc/html/man.css > doc/html/manual.html

deb/svgplease_${VERSION}_all.deb: ${SOURCES} ${TESTDATA} ${DOC} ${DEBIAN} doc/html/manual.html
	mkdir -p ${DEB_DIR}/source/code
	cp --preserve debian -R ${DEB_DIR}
	echo 1.0 > ${DEB_DIR}/source/format
	cp --preserve code/* -R ${DEB_DIR}/source/code
	cp --preserve doc -R ${DEB_DIR}/source/
	cp --preserve svgplease ${DEB_DIR}/source
	cp --preserve svgplease ${DEB_DIR}/source
	cp --preserve svgplease.fish ${DEB_DIR}/source
	cp --preserve svgplease.bash ${DEB_DIR}/source
	rm -rf $$(find ${DEB_DIR} -name '__pycache__' -or -name 'dist')
	rm -rf $$(find ${DEB_DIR} -name '*.swp' -or -name '*.pyc')
	bash -c 'cd ${DEB_DIR}; debuild; cd ../..'
	bash -c 'cd ${DEB_DIR}; debuild -S; cd ../..'

upload: deb/svgplease_${VERSION}_all.deb
	dput ppa:sapalskimichal/svgplease deb/svgplease_${VERSION}_source.changes

clean:
	rm deb -rf
	rm -f doc/html/manual.html

.PHONY: upload clean
