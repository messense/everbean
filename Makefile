default: build

.PHONY: build
build:
	python setup.py build

.PHONY: install
install:
	python setup.py install

.PHONY: test
	python setup.py test

.PHONY: clean
clean:
	python setup.py clean
	-python manage.py clear_cache
	find . -name '*.pyc' -print0 | xargs -0 rm -rf

