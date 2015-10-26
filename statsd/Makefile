
REPO := $(shell cd ../../..; pwd)

all: compose

compose:
	JUJU_REPOSITORY=$(REPO)/charms charm compose

clean:
	$(RM) -r $(REPO)/charms/trusty/statsd

.PHONY: all compose clean

