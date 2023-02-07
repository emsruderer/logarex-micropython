# logarex-micropython

A very simple, low cost, low power, utility that comes in handy for getting the data of your meter
in a convenient way.

A RP2 pico is used to read a Logarex-LK13BE80333 Power meter with a TTL IR-sensor (Volkszähler) 

IR-Schreib-Lesekopf, TTL-Interface
https://wiki.volkszaehler.org/hardware/controllers/ir-schreib-lesekopf-ttl-ausgang

Connected to one of the UARTs of the Pico with 9600 baud, 8bits, noparity, 1 stopbit 
Available with a browser via a simple web-page

serial = UART(1, baudrate=9600, bits=8, parity=None, stop=1, tx=Pin(4), rx=Pin(5))

It provides:
- the current power consumption
- kwh delivered to the grid
- day consumption (24h)
- week consumption (7d))
- month consumtion (30d)
- year consumption (365d)
- L1,L2,L3 data Volts and Amp

REMARK: you must know the PIN of the power meter and the meter must be set free, 
otherwise the data won't be available on the IR transmitter
Your energy company must provide you with that PIN.
