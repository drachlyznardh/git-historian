
all: check

check:
	@python3 setup.py check

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

.PHONY: all check install clean veryclean

