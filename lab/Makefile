# Check if sudo is installed and if the user is not root
# Use "sudo" if both are true
SUDO := $(shell if [ -x "$$(command -v sudo)" ] && [ "$$(id -u)" -ne 0 ]; then echo "sudo"; fi)

### Services (annet and netbox) control

build_annet:
	@cd ./annet && \
	cp -r ../scripts/netsshsetup ./netsshsetup && \
	docker build --no-cache -t annet . && \
	rm -rf ./netsshsetup

build_netbox:
	@git clone -b release https://github.com/netbox-community/netbox-docker.git
	@cp ./netbox-docker/docker-compose.yml ./netbox-docker/docker-compose.yml.bak
	@sed -i.bak 's/VERSION-v4.1-3.0.2/VERSION-v3.7/g' ./netbox-docker/docker-compose.yml
	@cd ./netbox-docker && docker-compose build --no-cache && cd ..

build: build_annet build_netbox

rebuild:
	rm -rf netbox-docker || true && \
	$(MAKE) build

services_stop:
	@cd ./netbox-docker && docker-compose down -v && cd ..

# Build and destroy architecture

lab00: services_stop
	@echo "Lab00 Cisco Basic Scenario is launching..." && \
	cp ./topologies/lab00_cisco_basic_scenario/docker-compose.override.yml ./netbox-docker/docker-compose.override.yml && \
	cd netbox-docker/ && docker-compose up -d && cd .. && \
	docker exec --user root netbox /opt/netbox/netbox/manage.py loaddata /home/ubuntu/src/netbox-dump.json && \
	echo "!!! Don't forget add Cisco IOS image into ../vm_images folder !!!"
	eval "docker exec -u root -t -i annet /bin/bash"

lab01: services_stop
	@cp ./topologies/lab01_frr-only-test/docker-compose.override.yml ./netbox-docker/docker-compose.override.yml && \
	cd topologies/lab01_frr-only-test && \
	$(SUDO) find operational_configs -mindepth 1 -not -name '.gitkeep' -delete || true && \
	cp -r default_configs/* operational_configs/ && \
	cd ../../netbox-docker/ && docker-compose up -d --build && cd .. && \
	docker exec --user root netbox /opt/netbox/netbox/manage.py loaddata /home/ubuntu/src/netbox-dump.json

lab02: services_stop
	cp ./topologies/lab02_dc_cisco/docker-compose.override.yml ./netbox-docker/docker-compose.override.yml && \
	cd netbox-docker/ && docker-compose up -d && cd .. && \
	docker exec --user root netbox /opt/netbox/netbox/manage.py loaddata /home/ubuntu/src/netbox-dump.json && \
	echo "!!! Don't forget add iol image into ./lab00_cisco_basic_scenario/src/ios-7200 folder !!!"

lab03: services_stop
	cp ./topologies/lab03_multivendor/docker-compose.override.yml ./netbox-docker/docker-compose.override.yml && \
	cd topologies/lab03_multivendor && \
	$(SUDO) find operational_configs -mindepth 1 -not -name '.gitkeep' -delete || true && \
	cp -r default_configs/* operational_configs/ && \
	cd ../../netbox-docker/ && docker-compose up -d --build && cd .. && \
	docker exec --user root netbox /opt/netbox/netbox/manage.py loaddata /home/ubuntu/src/netbox-dump.json

# Netbox utilities

netbox_export:
	@docker exec --user root netbox /opt/netbox/netbox/manage.py dumpdata -a -o /home/ubuntu/src/netbox-dump.json --exclude extras.cachedvalue --exclude extras.objectchange --exclude extras.report --exclude extras.script --exclude django_rq.queue --exclude auth.permission --exclude contenttypes.contenttype

netbox_import:
	@docker exec --user root netbox /opt/netbox/netbox/manage.py loaddata /home/ubuntu/src/netbox-dump.json

cc:
	isort topologies

style:
	pylint -j8 --score n --reports=no topologies && \
    flake8 topologies
