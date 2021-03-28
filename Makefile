venv: setup.py
	virtualenv venv

auror: venv
	. venv/bin/activate && pip install --editable .


docker-build: Dockerfile
	docker build -t hnicke/auror:latest .

docker-run: docker-build
	docker run --rm -it hnicke/auror:latest
