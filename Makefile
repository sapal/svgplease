VERSION=0.2
SOURCES=$(shell find code -name '*.py')
TESTDATA=$(shell find code -name '*.svg')
DOC=$(shell find doc)
DEB_DIR=deb/svgplease-${VERSION}

all: dist/svgplease_${VERSION}_all.deb

dist/svgplease_${VERSION}_all.deb: ${SOURCES} ${TESTDATA} ${DOC}
	mkdir -p ${DEB_DIR}/source/code
	cp --preserve debian -R ${DEB_DIR}
	mkdir -p dist
	echo 1.0 > ${DEB_DIR}/source/format
	cp --preserve code/* -R ${DEB_DIR}/source/code
	cp --preserve doc -R ${DEB_DIR}/source/
	cp --preserve svgplease ${DEB_DIR}/source
	cp --preserve svgplease ${DEB_DIR}/source
	cp --preserve svgplease.fish ${DEB_DIR}/source
	rm -rf $$(find ${DEB_DIR} -name '__pycache__' -or -name 'dist')
	rm -rf $$(find ${DEB_DIR} -name '*.swp' -or -name '*.pyc')
	bash -c 'cd ${DEB_DIR}; debuild; cd ../..'
	cp deb/svgplease_${VERSION}_all.deb dist

clean:
	rm dist deb -rf
