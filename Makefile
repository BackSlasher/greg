.PHONY: test

test:
	pylint greg -E
	python -m unittest discover -s tests
