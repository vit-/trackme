install-mux:
	@echo "TODO: fetch mux binary"

install-filebeat:
	curl -L -o /usr/sbin/filebeat https://github.com/vit-/trackme/releases/download/v7.5.1/filebeat
	chmod +x /usr/sbin/filebeat

install-metricbeat:
	curl -L -o /usr/sbin/metricbeat https://github.com/vit-/trackme/releases/download/v7.5.1/metricbeat
	chmod +x /usr/sbin/metricbeat

install-trackme:
	python3 -m pip install -e src/

install-tools:
	apt-get update
	apt-get install -y fail2ban screen tmux ppp vim python3-pip
	apt-get clean

install-all: install-mux install-filebeat install-metricbeat install-trackme install-tools

config-initial:
	cp -r conf_fs/* /
	mkdir -p /var/beats/metricbeat
	mkdir -p /var/beats/filebeat
	mkdir -p /var/trackme
	chown -Rf pi:pi /var/beats
	chown -Rf pi:pi /var/trackme
	usermod -a -G tty pi

config-beats:
ifeq ($(wildcard beats.personal.yaml),)
	$(error beats.personal.yaml is missing, see beats.personal.reference.yaml for reference)
else
	echo "\n" >> /etc/beats/filebeat.yaml
	echo "\n" >> /etc/beats/metricbeat.yaml
	cat beats.personal.yaml >> /etc/beats/filebeat.yaml
	cat beats.personal.yaml >> /etc/beats/metricbeat.yaml
endif

config-all: config-initial config-beats

enable-mux:
	systemctl enable mux

enable-filebeat:
	systemctl enable filebeat

enable-metricbeat:
	systemctl enable metricbeat

enable-trackme:
	systemctl enable trackme

enable-all: enable-mux enable-filebeat enable-metricbeat enable-trackme

install: install-all config-all enable-all
