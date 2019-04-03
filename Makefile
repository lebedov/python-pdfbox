PYTHON := `which python`

NAME = python-pdfbox
VERSION = $(shell $(PYTHON) -c 'import setup; print setup.VERSION')

.PHONY: package build develop install test clean

package:
	$(PYTHON) setup.py sdist --formats=gztar bdist_wheel

upload: | package
	twine upload dist/*
	
build:
	$(PYTHON) setup.py build

develop:
	$(PYTHON) setup.py develop

install:
	$(PYTHON) setup.py install

test:
	$(PYTHON) -m unittest tests/test_pdfbox.py

clean:
	$(PYTHON) setup.py clean
	rm -f dist/*
