#!/usr/bin/env bash

# Script for installing pico-ducky on a Raspberry Pi Pico W
# Just plug in the Pi, and let the script guide you
# Should work in most versions of Ubuntu

set -e
SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
CACHEDIR=/tmp/pico-ducky-cache
mkdir -p $CACHEDIR
cd $CACHEDIR
echo "Downloading CircuitPython 8.0.5"
set +e;
ls adafruit-circuitpython-raspberry_pi_pico_w-en_US-8.0.5.uf2 &> /dev/null
CACHED=$?
set -e
if [ "$CACHED" -eq 0 ]
then
	echo "Using cached adafruit-circuitpython-raspberry_pi_pico_w-en_US-8.0.5.uf2"
else
	wget -nv https://adafruit-circuit-python.s3.amazonaws.com/bin/raspberry_pi_pico_w/en_US/adafruit-circuitpython-raspberry_pi_pico_w-en_US-8.0.5.uf2
fi

waitForFile() {
	FILETOWAITFOR=$1
	set +e
	while true
	do
		ls $FILETOWAITFOR &> /dev/null
		if [ "$?" -eq 0 ]
		then
			break
		fi
		echo "Waiting for $FILETOWAITFOR to appear..."
		sleep 2
	done
	set -e
}

echo "Downloading CircuitPython bundle 8.x"
cd $CACHEDIR
set +e
ls adafruit-circuitpython-bundle-8.x-mpy-20230616.zip &> /dev/null
CACHED=$?
set -e
if [ "$CACHED" -eq 0 ]
then
	echo "Using cached adafruit-circuitpython-bundle-8.x-mpy-20230616.zip"
else
	wget -nv https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/download/20230616/adafruit-circuitpython-bundle-8.x-mpy-20230616.zip
fi
unzip -q -o *.zip

echo "Downloading flash_nuke.uf2"
set +e
ls flash_nuke.uf2 &> /dev/null
CACHED=$?
set -e
if [ "$CACHED" -eq 0 ]
then
	echo "Using cached flash_nuke.uf2"
else
	wget -nv https://datasheets.raspberrypi.com/soft/flash_nuke.uf2
fi

echo "Hold the button on the Pico W and plug it in so it shows up as mass storage device \"RPI-RP2\""
waitForFile '/media/*/RPI-RP2'

echo "Installing flash_nuke"
cd /media/*/RPI-RP2
cp $CACHEDIR/flash_nuke.uf2 .
echo "Done"

echo "Waiting for the Pico W to reboot..."
sleep 3
waitForFile '/media/*/RPI-RP2'


echo "Installing CircuitPython image"
cd /media/*/RPI-RP2
cp $CACHEDIR/adafruit-circuitpython-raspberry_pi_pico_w-en_US-8.0.5.uf2 .
echo "Done"

echo "Waiting for the Pico W to reboot again..."
waitForFile	'/media/*/CIRCUITPY'

echo "Installing pico-ducky and friends"
cd /media/*/CIRCUITPY
CPYDIR=`pwd`
CPBUNDLEDIR=$CACHEDIR/adafruit-circuitpython-bundle-8.x-mpy-20230616/
cp -r $CPBUNDLEDIR/lib/adafruit_hid lib/
cp -r $CPBUNDLEDIR/lib/adafruit_debouncer.mpy lib/
cp -r $CPBUNDLEDIR/lib/adafruit_ticks.mpy lib/
cp -r $CPBUNDLEDIR/lib/asyncio lib/
cp -r $CPBUNDLEDIR/lib/adafruit_wsgi lib/
cp -r $SCRIPTDIR/boot.py .
cp -r $SCRIPTDIR/duckyinpython.py .
cp -r $SCRIPTDIR/code.py .
cp -r $SCRIPTDIR/webapp.py .
cp -r $SCRIPTDIR/wsgiserver.py .
echo "Done"

printf "\nIf you want wireless AP mode enabled, type in SSID now. Press [Enter] to continue with AP disabled\n"
read SSID
if [ -z "$SSID" ]
then
	echo "Leaving AP disabled"
else
	echo "Type in password:"
	read PSK
	if [ -z "$PSK" ]
	then
		echo "Password was empty. Leaving AP disabled"
	else
		echo "Installing AP settings..."
		echo "secrets = { 'ssid' : \"$SSID\", 'password' : \"$PSK\" }" > $CPYDIR/secrets.py
	fi
fi

printf "\nThe device is now ready, and you may install your playload.dd in $CPYDIR\n"
