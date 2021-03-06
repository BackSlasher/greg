.PHONY: test prep clean localserver

test:
	bin/pip install -e .[test]
	bin/python -m pylint greg -E
	bin/python -m unittest discover -s tests

localserver:
	DEBUG=true bin/python -m greg.server

prep:
	bin/pip freeze | grep -v '^-e' | tee requirements.txt >/dev/null
	zip greg.zip -r application.py config.yaml greg setup.py requirements.txt README.rst
	realpath greg.zip
	git rev-parse --short HEAD

clean:
	rm -f requirements.txt greg.zip
