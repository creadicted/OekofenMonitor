# This is a sample Python script.

# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import configparser
import json
import urllib.request
from datetime import datetime
import logging

# Setup Logger
from influxdb import InfluxDBClient

logger = logging.getLogger('oe')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('oekofetch.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

# Config
config = configparser.ConfigParser()
config.sections()
config.read('oekofen-fetch.cfg')

# Define Parameters for Heating Unit
heater_ip = config['HEATER']['ip']
heater_port = config['HEATER']['port']
heater_user = config['HEATER']['user']
heater_path = heater_ip + ":" + str(heater_port) + "/" + heater_user + "/all"

# Configure InfluxDB connection variables
host = config['InfluxDb']['host']
port = config['InfluxDb']['port']
user = config['InfluxDb']['user']
password = config['InfluxDb']['password']
dbname = config['InfluxDb']['dbname']

# Connect to Influx Database
client = InfluxDBClient(host, port, user, password, dbname)

script_execution = datetime.now()


def print_hi(name):
    print(heater_path)
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Strg+F8 to toggle the breakpoint.


# Check if the value is a number, otherwise it's a String
def num(s):
    try:
        return float(s)
    except ValueError:
        return s


def fetch_data_from_heater():
    res = urllib.request.urlopen(heater_path)
    heater_data = res.read().decode("cp1252")
    heater_json = json.loads(heater_data)
    return heater_json

# This method preprocess the data.
# For example the heater encodes 100 degrees as "1000".
# So temperature values need to be divided by 10.
def cleanup_data(data):
    cleaned = []
    for key in data:
        if isinstance(data[key], dict):
            cleanup_data(data[key])
            for attribute, value in data[key].items():
                w = num(value)
                if "mode" in str(attribute):
                    w = int(w)
                elif "_prg" in str(attribute):
                    w = int(w)
                elif str(attribute) == "L_state":
                    w = int(w)
                elif "temp_" in str(attribute):
                    w = float(w) / 10
                elif "_temp" in str(attribute):
                    w = float(w) / 10
                elif "ambient" in str(attribute):
                    w = float(w) / 10
                elif "L_tp" in str(attribute):
                    w = float(w) / 10
                elif "L_day" in str(attribute):
                    w = float(w) / 10
                elif "L_yesterday" in str(attribute):
                    w = float(w) / 10
                elif "L_sp" in str(attribute):
                    w = float(w) / 10
                elif str(attribute) == "L_flow":
                    w = float(w) / 100
                elif str(attribute) == "L_pwr":
                    w = float(w) / 10
                if "?" in str(w):
                    w = str(w).replace("u?e", "usse")
                    w = str(w).replace("?ber", "ueber")
                    w = str(w).replace("t?t", "taet")

                if w == "":
                    w = " "

                if w == "true":
                    w = 1
                    attribute = attribute + "_mod"
                if w == "false":
                    w = 0
                    attribute = attribute + "_mod"
                cleaned.append([str(key), str(attribute), w])

    return cleaned


def insert_into_db(measurement, name, value):
    new_entry = [
        {
            "measurement": measurement,
            "fields": {
                name: value
            }
        }
    ]
    client.write_points(new_entry)

def insert_list_to_db(data):
    for key in data:
        insert_into_db(key[0], key[1], key[2])

if __name__ == '__main__':
    logger.info('Execute Fetch')
    json = fetch_data_from_heater()
    cleaned = cleanup_data(json)
    insert_list_to_db(cleaned)