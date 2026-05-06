.PHONY: install lint test run docker-build compose-up compose-down

install:
	python -m pip install --upgrade pip
	python -m pip install -r requirements-dev.txt

lint:
	python -m flake8 app tests

test:
	python -m pytest tests/

run:
	python -m app.main

docker-build:
	sudo docker build -t ci-cd-lab:local .

compose-up:
	sudo docker compose up -d --build

compose-down:
	sudo docker compose down
