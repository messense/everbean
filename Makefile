default: build

.PHONY: build
build:
	python setup.py build

.PHONY: install
install:
	python setup.py install

.PHONY: test
test:
	python setup.py test

.PHONY: assets
assets:
	python manage.py assets build

.PHONY: clean
clean:
	python setup.py clean
	-python manage.py clear_cache
	-python manage.py assets clean
	find . -name '*.pyc' -print0 | xargs -0 rm -rf

