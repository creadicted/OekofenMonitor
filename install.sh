#!/bin/bash
# This script will install dependencies for the Oekofen Monitoring tool.

apt-get update

## Install influxdb
apt-get -y install influxdb
apt-get -y install influxdb-client

## Once installed, start the influxdb service.
systemctl start influxdb

# Configure the InfluxDB Server
influx -execute "create database oekofen"
influx -execute "SHOW DATABASES"
influx -execute "CREATE USER pellematic WITH PASSWORD 'smart' WITH ALL PRIVILEGES"
influx -execute "grant all privileges on oekofen to pellematic"

# Install Grafana for Pi
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
sudo apt-get install -y grafana
### Enable the Grafana server
sudo /bin/systemctl enable grafana-server
### Start the Grafana server
sudo /bin/systemctl start grafana-server

apt-get -y install python3-influxdb

# Install Python dependencies
pip3 install python-dotenv

# Restart
shutdown -r now