.PHONY: test

test:
	python -m unittest discover -s tests
	pylint greg -E
