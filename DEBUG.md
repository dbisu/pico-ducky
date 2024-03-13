# Instructions on how to collect debug logs

* On Windows, use [PuTTY](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html) to connect to the debug serial port (commonly COM3, but could vary on your machine).

* On Linux, use minicom (minicom -b 115200 -o -D /dev/ttyACM0, where ttyACM0 corresponds to your device).
  * On Ubuntu: `sudo apt install minicom`
