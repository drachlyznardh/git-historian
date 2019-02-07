
all: check run

run:
	@PYTHONPATH=src python3 -m githistorian -n30

check:
	@python3 setup.py check

build:
	@python3 setup.py build

dist:
	@python3 setup.py sdist

install:
	@pip3 install --user .

