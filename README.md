# Overview
TrackMe aims to be an easy to use geo data and telemetry collector for a DIY GPS trackers.

At a high level solution works as follows. A python app collects geo data every 10 seconds 
and stores it in a file. [Filebeat](https://www.elastic.co/products/beats/filebeat) ships this
data to remote [Elasticsearch](https://www.elastic.co/products/elasticsearch). 
Additionally, [Metricbeat](https://www.elastic.co/products/beats/metricbeat) ships basic node metrics:
CPU, network and disk utilization. 

With such configuration geo data is preserved even if Internet connection is lost. 
It is uploaded with no losses when connection is available again.  

# Hardware
The project is implemented and tested with the following hardware:
- Raspberry Pi Zero
- Raspberry Pi 3
- Adafruit [Fona 808](https://www.adafruit.com/product/2542) GSM + GPS module

It should be straight forward to adapt the project to other similar hardware.

# Software prerequisites
TrackMe was tested on Raspbian Stretch Lite 2019-04-08.
There are issues with Raspbian Buster - Internet connection does not start automatically 
on system boot.

TrackMe leverages [GSM 07.10 tty multiplexor](https://www.kernel.org/doc/html/latest/driver-api/serial/n_gsm.html),
which should be embedded into kernel or loaded as a kernel module.
Detailed instructions on kernel compilation can be found in [official docs](https://www.raspberrypi.org/documentation/linux/kernel/building.md).
In the kernel configuration menu navigate to "Device Drivers" > "Character devices" 
and select "GSM MUX line discipline support (EXPERIMENTAL)".

Note: don't forget to disable Linux console and enable serial port on Raspberry, docs [here](https://www.raspberrypi.org/documentation/configuration/uart.md).
