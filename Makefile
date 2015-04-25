
all: check run

run:
	@PYTHONPATH=src python -m githistorian -n30

check:
	@python setup.py check

build:
	@python setup.py build

install:
	@python setup.py install

