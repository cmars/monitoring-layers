
REPO := $(shell cd ../../..; pwd)

LOCAL_RELEASE=0.9.4.2

all: influxdb-local compose

influxdb-local: files/influxdb_$(LOCAL_RELEASE)_amd64.deb files/influxdb_current.deb

files/influxdb_current.deb: files/influxdb_$(LOCAL_RELEASE)_amd64.deb
	(cd files; ln -s $(shell basename $<) $(shell basename $@))

files/influxdb_$(LOCAL_RELEASE)_amd64.deb:
	wget -O $@ https://s3.amazonaws.com/influxdb/influxdb_$(LOCAL_RELEASE)_amd64.deb

compose:
	JUJU_REPOSITORY=$(REPO)/charms charm compose

clean:
	$(RM) -r $(REPO)/charms/trusty/influxdb
	$(RM) files/influxdb_current.deb

.PHONY: all compose clean influx-local

