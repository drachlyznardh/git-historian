
all: check run

run:
	@PYTHONPATH=src python -m githistorian -n30

check:
	@python setup.py check

build:
	@python setup.py build

dist:
	@python setup.py sdist

install:
	@python setup.py install

