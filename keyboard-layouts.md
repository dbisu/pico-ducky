## How to install non-US keyboard layouts

Clone Circuitpython_Keyboard_Layouts  
`git clone https://github.com/Neradoc/Circuitpython_Keyboard_Layouts`

`cd Circuitpython_Keyboard_Layouts`

Install dependencies  
`pip3 install -r requirements-modules.txt`

Install build dependencies  
`pip3 install -r requirements-dev.txt`

Build layouts  
`python3 build.py`

Copy libraries to pico  
`cp _build/circuitpython-keyboard-layouts-6.x-mpy-<date>/lib/*.mpy /<Pico mount point>/lib`

Update duckyinpython.py  
Change  
`kblayout="US"`  
to  
`kblayout="<keyboard layout>"`  

Update `if kblayout ==` block to include the new keyboard layout if not already included
