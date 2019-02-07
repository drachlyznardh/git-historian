
all: check run

run:
	@PYTHONPATH=src python3 -m githistorian -n30

check:
	@python3 setup.py check

build:
	@python3 setup.py build

bdist:
	@python3 setup.py bdist

sdist:
	@python3 setup.py sdist

install:
	@pip3 install --user .

clean:
	@python3 setup.py clean

.PHONY: all install clean

