import os
import pwd
import shutil
from subprocess import check_call

from charmhelpers.core import hookenv, host
from charmhelpers.core.templating import render
from charmhelpers.fetch import apt_update, apt_install
from charms.reactive import hook, when, when_not, is_state, set_state, remove_state
from charms.reactive.bus import get_states


@hook('install')
def install():
    if is_state('influxdb.available'):
        return
    check_call(['dpkg', '-i', 'files/influxdb_current.deb'])


@hook('update')
def update():
    if is_state('influxdb.started'):
        host.service_stop('influxdb')
    check_call(['dpkg', '-i', 'files/influxdb_current.deb'])
    if is_state('influxdb.started'):
        host.service_start('influxdb')


@hook('config-changed')
def config_changed():
    config = hookenv.config()
    for port_name in ('api_port', 'admin_port', 'graphite_port'):
        if config.changed(port_name):
            if config.previous(port_name):
                hookenv.close_port(config.previous(port_name))
            hookenv.open_port(config[port_name])
    set_state('influxdb.configured')


@when('influxdb.start')
@when_not('influxdb.started')
def start_influxdb():
    host.service_start('influxdb')
    set_state('influxdb.started')


@when('influxdb.started')
@when_not('influxdb.start')
def stop_influxdb():
    host.service_stop('influxdb')
    remove_state('influxdb.started')


@when('influxdb.configured')
def setup():
    remove_state('influxdb.start')
    if is_state('influxdb.started'):
        host.service_stop('influxdb')

    config = hookenv.config()
    render(source="config.toml",
        target="/opt/influxdb/shared/config.toml",
        owner="root",
        perms=0o644,
        context={
            'cfg': config,
        })

    set_state('influxdb.start')
    if is_state('influxdb.started'):
        host.service_start('influxdb')
    else:
        hookenv.status_set('maintenance', 'starting influxdb')


@when('influxdb.started')
def influxdb_started():
    config = hookenv.config()
    for port_name in ('api_port', 'admin_port', 'graphite_port'):
        hookenv.open_port(config[port_name])
    hookenv.status_set('active', 'ready')
