.PHONY: test prep clean localserver

test:
	bin/pip install -e .[test]
	bin/python -m pylint greg -E
	bin/python -m unittest discover -s tests

localserver:
	DEBUG=true bin/python -m greg.server

prep:
	set -e ;\
	. bin/activate ;\
	pip freeze | grep -v '^-e' | tee requirements.txt >/dev/null ;\
	zip greg.zip -r application.py config.yaml greg setup.py requirements.txt README.rst

clean:
	rm -f requirements.txt greg.zip
