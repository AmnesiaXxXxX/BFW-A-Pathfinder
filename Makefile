IMAGE_NAME ?= ghcr.io/amnesiaxxxxx/bfw-a-pathfinder:latest

.PHONY: build push run check install-deps pycheck

build:
	docker build -t $(IMAGE_NAME) .

push:
	docker buildx build --platform linux/amd64 -t $(IMAGE_NAME) . --push

install-deps:
	pip install --upgrade pip \
		&& pip install uv \
		&& uv sync --frozen

pycheck:
	uv run pylint -f=github --recursive=y src/ main.py

run:
	docker run --rm -it \
		-e DISPLAY=$$DISPLAY \
		--memory=512m \
		--cpus="4" \
		--device /dev/dri:/dev/dri \
		-v /tmp/.X11-unix:/tmp/.X11-unix \
		$(IMAGE_NAME)