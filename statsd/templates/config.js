{
{% if influx %}
  influxdb: {
    host: '{{influx.hostname}}', // InfluxDB host (default 127.0.0.1)
    port: {{influx.port}}, // InfluxDB port (default 8086)
    database: 'data',  // InfluxDB db instance (required)
    username: '{{influx.user}}', // InfluxDB db username (required)
    password: '{{influx.password}}', // InfluxDB db password (required)
    flush: {
      enable: true // enable regular flush strategy (default true)
    },
    proxy: {
      enable: false, // enable the proxy strategy (default false)
      suffix: 'raw', // metric name suffix (default 'raw')
      flushInterval: 1000
    }
  },
{% endif %}
  backends: [
{% if influx %}
    'statsd-influxdb-backend',
{% endif %}
    './backends/console'
  ],
  port: {{cfg.port}}, // statsD port
  debug: true,
  legacyNamespace: false
}
