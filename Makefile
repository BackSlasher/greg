.PHONY: test prep

test:
	. bin/activate
	pip install -e .[test]
	pylint greg -E
	python -m unittest discover -s tests

prep:
	pip freeze | grep -v '^-e' | tee requirements.txt >/dev/null
