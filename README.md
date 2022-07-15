# Instructions

This instruction is as simple as possible but I still expect some knowledge:

* The json API is enabled (You can do that on the terminal of your device).
* You have a Raspberry Pi or other device that you can access via ssh, add files and execute them.

Both things are searchable.

## 1. Install all required dependencies

To install everything needed a simple 'install.sh' script is provided following dependencies:

* influxdb
  creates a database `oekofen` with the user `pellematic` and the password `smart`
* Grafana
  The setup is compatible with the original project [oekofen-spy](https://gitlab.com/p3605/oekofen-spy) developed by
  Peter Fürle.

Upload the install.sh file to your pi and execute
> sudo ./install.sh

## 2. Upload the Data Grabber

Based on the original project [oekofen-spy](https://gitlab.com/p3605/oekofen-spy) part of this repository is
the `oekofen-fetch.py` file, and a configuration file in which you need to set the ip, port and the user of your device
in your local network.

Example `oekofen-fetch.cfg`:

```
[HEATER]
ip = http://192.168.1.1
port = 4321
user = aT4m

[InfluxDb]
host = 127.0.0.1
port = 8086
user = pellematic
password = smart
dbname = oekofen
```

A `oekofen-fetch.cfg` sample file is provided in this repository

## 3. Add a cronjob to execute the data fetcher

The script takes the data from the json and inserts it in to the influx database. A cronjob is a task the device will
execute regularly. To add a script to the list of tasks edit `/etc/crontab`. Either use editor for files over ssh or use
the terminal to ssh in to your device and execute:
> sudo nano /etc/crontab

You will see something like this

```
# Example of job definition:
# .---------------- minute (0 - 59)
# |  .------------- hour (0 - 23)
# |  |  .---------- day of month (1 - 31)
# |  |  |  .------- month (1 - 12) OR jan,feb,mar,apr ...
# |  |  |  |  .---- day of week (0 - 6) (Sunday=0 or 7) OR sun,mon,tue,wed,thu,fri,sat
# |  |  |  |  |
# *  *  *  *  * user-name command to be executed
17 *	* * *	root    cd / && run-parts --report /etc/cron.hourly
25 6	* * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6	* * 7	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6	1 * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
```

Add the line

```
*/1 *  * * * pi   /usr/bin/python3 /home/pi/oekofen-fetch.py
```

It will call the script every minute.

## 4. Login in to Graphana

The default user is `admin` with the password `admin`. You need to change it after your first login.

### 4.1 Add Influx DB as a data source

Configuration > Add data source > InfluxDB
Add the values used in the setup:

```
URL = http://localhost:8086
Database = oekofen
User = pellematic
password = smart
HTTP Method =  GET
```

# Additional Setup

## To Open the graphana ui on startup of the device:

1. You’ll need to configure the Chromium browser to open websites in full screen. Open a terminal and type this to get
   to the configuration setting:

> cd .config

2. That should open the hidden configuration directory in your Pi user directory. Next, create the lxsession and lxde-pi
   directories. If you receive an error, then this folder already exists but if you’re setting up a brand new Pi – it
   won’t be there yet.

> sudo mkdir -p lxsession/LXDE-pi

4. This next line opens a folder called autostart.

> sudo nano lxsession/LXDE-pi/autostart

5. Paste the code below into the nano text editor. On the very last line, change the URL to the website you want to
   automatically open on startup or after a reboot.

> @lxpanel --profile LXDE-pi
> @pcmanfm --desktop --profile LXDE-pi
> #@xscreensaver -no-splash
> point-rpi
> @chromium-browser --start-fullscreen --start-maximized http://localhost:3000/
>

6. Restart

> sudo shutdown -r now