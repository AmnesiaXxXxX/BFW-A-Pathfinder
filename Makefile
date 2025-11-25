repo = ghcr.io/amnesiaxxxxx/bfw-a-pathfinder:latest

.PHONY: build push run

build:
	docker build -t $(repo) .

push:
	docker buildx build --platform linux/amd64 -t $(repo) . --push

run:
	docker run --rm -it \
		-e DISPLAY=$$DISPLAY \
		--memory=512m \
		--cpus="4" \
		--device /dev/dri:/dev/dri \
		-v /tmp/.X11-unix:/tmp/.X11-unix \
		$(repo)
