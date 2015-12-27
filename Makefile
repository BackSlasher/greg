.PHONY: test prep clean

test:
	. bin/activate
	pip install -e .[test]
	pylint greg -E
	python -m unittest discover -s tests

prep:
	pip freeze | grep -v '^-e' | tee requirements.txt >/dev/null
	zip greg.zip -r application.py config.yaml greg setup.py requirements.txt README.rst

clean:
	rm -f requirements.txt greg.zip
