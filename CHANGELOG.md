# 1.0.0
Initial version. Key highlights:
- Internet connection starts on system boot (PPPD)
- /dev/serial0 is multiplexed to 4 devices: /dev/fona[0-3]
- Geo data is collected to a file
- Filebeat ships geo data
- Metricbeat ships basic node metrics: CPU, network and disk utilization
