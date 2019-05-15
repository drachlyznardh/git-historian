
all: check

check:
	@python3 setup.py check

scheck:
	@python3 -m venv /tmp/gh-stest
	@. /tmp/gh-stest/bin/activate && pip3 install dist/githistorian-$(shell cat VERSION).tar.gz
	@. /tmp/gh-stest/bin/activate && githistorian --version

install:
	@pip3 install --verbose --user .

clean:
	@python3 setup.py clean

veryclean: clean
	@rm -rf dist/ build/
	@find . -name '*.egg-info' | xargs rm -rf
	@find . -name __pycache__ | xargs rm -rf

dist:
	@python3 setup.py sdist bdist_wheel

publish: veryclean dist
	@python3 -m twine upload dist/*.whl dist/*.tar.gz

.PHONY: all check install clean veryclean dist

