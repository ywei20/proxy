IMAGE_NAME ?= proxy
IMAGE_TAG ?= latest
PORT ?= 8000

.PHONY: install install-dev run test docker-build docker-run docker-stop

install:
	python -m pip install -r requirements.txt

install-dev:
	python -m pip install -r requirements-dev.txt

run:
	uvicorn app.main:app --host 0.0.0.0 --port $(PORT) --reload

test:
	python -m pytest

docker-build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

docker-run:
	docker run --rm --name $(IMAGE_NAME) -p $(PORT):8000 $(IMAGE_NAME):$(IMAGE_TAG)

docker-stop:
	docker stop $(IMAGE_NAME)
