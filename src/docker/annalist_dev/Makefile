
BASE=ubuntu
IMAGE=annalist_dev
DATA_CONTAINER=annalist_site
RELEASE=$(shell annalist-manager version)
# RELEASE_PREFIX=
HOSTPORT=8000
GUESTPORT=8000

base-shell:
	docker run --rm -it $(BASE) bash

clean:
	$(RM) .build

all: clean build

build: .build

.build: Dockerfile
	docker build --rm=false -t $(IMAGE):$(RELEASE) .
	touch .build

shell: build
	docker run --rm -it -p $(HOSTPORT):$(GUESTPORT) --volumes-from=$(DATA_CONTAINER) $(IMAGE):$(RELEASE) bash

inspect: build
	docker run --rm -it --volumes-from=$(DATA_CONTAINER) $(IMAGE):$(RELEASE) bash

run: build
	# docker run --rm -it -p $(HOSTPORT):$(GUESTPORT) $(IMAGE)
	docker run --rm -it -p $(HOSTPORT):$(GUESTPORT) --volumes-from=$(DATA_CONTAINER) $(IMAGE):$(RELEASE) annalist-manager runserver

push: build
	docker tag -f $(IMAGE):$(RELEASE) gklyne/$(IMAGE):$(RELEASE)
	docker push gklyne/$(IMAGE):$(RELEASE)
	docker tag -f $(IMAGE):$(RELEASE) gklyne/$(IMAGE):latest
	docker push gklyne/$(IMAGE)

# Declare non-file targets
.PHONY: base-shell all clean build shell inspect run push 

