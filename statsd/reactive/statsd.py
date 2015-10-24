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
    if is_state('statsd.available'):
        return
    apt_update()
    apt_install(['nodejs', 'npm', 'git'])
    check_call(['git', 'clone', 'https://github.com/etsy/statsd.git'], cwd='/opt')
    check_call(['npm', 'install', 'statsd-influxdb-backend'])
    
    shutil.copyfile('files/upstart', '/etc/init/statsd.conf')


@hook('update')
def update():
    if is_state('statsd.started'):
        host.service_stop('statsd')
    apt_update()
    apt_upgrade(['nodejs', 'npm', 'git'])
    check_call(['git', 'pull', 'origin', 'master'], cwd='/opt/statsd')
    check_call(['npm', 'update', 'statsd-influxdb-backend'])
    if is_state('statsd.started'):
        host.service_start('statsd')


@hook('config-changed')
def config_changed():
    config = hookenv.config()
    if config.changed('port'):
        if config.previous('port'):
            hookenv.close_port(config.previous('port'))
        hookenv.open_port(config['port'], protocol='UDP')
    if not is_state('influxdb.connected'):
        render(source="config.js",
            target="/opt/statsd/config.js",
            owner="root",
            perms=0o644,
            context={
                'cfg': config,
            })
    set_state('statsd.configured')


@when('statsd.start')
@when_not('statsd.started')
def start_statsd():
    host.service_start('statsd')
    set_state('statsd.started')


@when('statsd.started')
@when_not('statsd.start')
def stop_statsd():
    host.service_stop('statsd')
    remove_state('statsd.started')


@when('statsd.configured', 'influxdb.connected', 'influxdb.api.available')
def setup(db, _):
    remove_state('statsd.start')
    if is_state('statsd.started'):
        host.service_stop('statsd')

    config = hookenv.config()
    render(source="config.js",
        target="/opt/statsd/config.js",
        owner="root",
        perms=0o644,
        context={
            'cfg': config,
            'influx': db,
        })

    set_state('statsd.start')
    if is_state('statsd.started'):
        host.service_start('statsd')
    else:
        hookenv.status_set('maintenance', 'starting statsd')


@when('statsd.started')
def statsd_started():
    config = hookenv.config()
    hookenv.open_port(config['port'], protocol='UDP')
    hookenv.status_set('active', 'ready')
