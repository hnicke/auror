venv: setup.py
	virtualenv venv

auror: venv
	. venv/bin/activate && pip install --editable .


