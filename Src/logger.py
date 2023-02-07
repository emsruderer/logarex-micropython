from machine import UART, Pin
from machine import RTC
import time
import _thread
import network
import socket
import sys
import struct
import ubinascii
import logging
import wlan

logging.basicConfig(logging.INFO)

def reset():
    machine.reset()

wlan = wlan.Wifi()

serial = UART(1, baudrate=9600, bits=8, parity=None, stop=1, tx=Pin(4), rx=Pin(5))
serial.init()

STOP = False
LOGLGT = 676
data = bytearray(LOGLGT)

baton = _thread.allocate_lock()

def read_data():
      global STOP
      while not STOP:
          n = serial.any()
          if n :
              baton.acquire()
              lgt = serial.readinto(data)
              baton.release()
          if STOP: return
          time.sleep_ms(10)
      if STOP: return
     
def get_data():
    try:
        baton.acquire()
        data_str = str(data,"utf-8")
        baton.release()
        data_lst = data_str.splitlines()
        return data_lst
    except UnicodeError as err:
        logging.exception(err,"UnicodeError")

def processdata(lijst):
    meting = {
        'Nu': 'fake',
        'Net': '11',
        'Dag': '8',
        'Week': '50',
        'Maand': '200',
        'Jaar': '2500',
        'Stand':'14000',
        'L1-Volt' : '230',
        'L2-Volt' : '230',
        'L3-Volt' : '230',
        'L1-Amp' : '1.0',
        'L2-Amp' : '1.0',
        'L3-Amp' : '1.0'
    }
    for value in lijst:
        if value.startswith('1-0:16.7.0'):
            meting['Nu'] = value.split('(')[1].split('*')[0]
        elif value.startswith('1-0:2.8.0'):
            meting['Net'] = value.split('(')[1].split('*')[0]
        elif value.startswith('1-0:1.8.0*96'):
            meting['Dag'] = value.split('(')[1].split('*')[0]
        elif value.startswith('1-0:1.8.0*97'):
            meting['Week'] = value.split('(')[1].split('*')[0]
        elif value.startswith('1-0:1.8.0*98'):
            meting['Maand'] = value.split('(')[1].split('*')[0]
        elif value.startswith('1-0:1.8.0*99'):
            meting['Jaar'] = value.split('(')[1].split('*')[0]
        elif value.startswith('1-0:1.8.0*100'):
            meting['Stand'] = value.split('(')[1].split('*')[0]
        elif value.startswith('1-0:32.7.0'):
            meting['L1-Volt'] = value.split('(')[1].split('*')[0]
        elif value.startswith('1-0:72.7.0'):
            meting['L2-Volt'] = value.split('(')[1].split('*')[0]
        elif value.startswith('1-0:52.7.0'):
            meting['L3-Volt'] = value.split('(')[1].split('*')[0]
        elif value.startswith('1-0:31.7.0'):
            meting['L1-Amp'] = value.split('(')[1].split('*')[0]
        elif value.startswith('1-0:71.7.0'):
            meting['L2-Amp'] = value.split('(')[1].split('*')[0]
        elif value.startswith('1-0:51.7.0'):
            meting['L3-Amp'] = value.split('(')[1].split('*')[0]
        for key in meting:
            if meting[key].find('0')>=0 :
                logging.debug("found:"+ str(meting[key]))
                meting[key] = meting[key].lstrip('0')
    return meting


def show_meting(meting):
    for value in meting:
        w = meting[value].split('*')
        logging.info(f'{value}\t{float(w[0]):{7}.{1}f} {w[1]}')


def make_html(d):
    html_s = '''<!DOCTYPE html>
    <html>
        <head>
        <meta http-equiv="refresh" content="10" >
        <style>
           body { font-family: "Lucida Console", "Courier New", monospace;
                  font-size: 2.0em; background-color: lightblue;
           }
            table { table-layout: auto;
                    width: 30%;
                    padding: 10px;
                    border: 10px solid gray;
                    margin: 10;
                    font-size: 2.0em;
                    
           }
        </style>
        <title>Logarex stroommeter</title>
        </head>
        <body><h1>Logarex stroommeter</h1>
            <table>
            <tr><th align="left">Periode</th><th align="right">Verbruik</th><th align="left">Eenheid</th></tr>
    '''
    html_r = ('<tr><td>Nu</td><td align="right">' + d['Nu'] + '</td><td>Watt</td></tr>'
    +  '<tr><td>Net</td><td align="right">' + d['Net'] + '</td><td>kWh</td></tr>'
    +  '<tr><td>Dag</td><td align="right">' + d['Dag'] + '</td><td>kWh</td></tr>'
    +  '<tr><td>Week</td><td align="right">' + d['Week'] + '</td><td>kWh</td></tr>'
    +  '<tr><td>Maand</td><td align="right">' + d['Maand'] + '</td><td>kWh</td></tr>'
    +  '<tr><td>Jaar</td><td align="right">' + d['Jaar'] + '</td><td>kWh</td></tr>'
    +  '<tr><td>Stand</td><td align="right">' + d['Stand'] + '</td><td>kWh</td></tr>'
    +  '<tr><td>L1-Volt</td><td align="right">' + d['L1-Volt'] + '</td><td>Volt</td></tr>'
    +  '<tr><td>L2-Volt</td><td align="right">' + d['L2-Volt'] + '</td><td>Volt</td></tr>'
    +  '<tr><td>L3-Volt</td><td align="right">' + d['L3-Volt'] + '</td><td>Volt</td></tr>'
    +  '<tr><td>L1-Amp</td><td align="right">' + d['L1-Amp'] + '</td><td>Amp</td></tr>'
    +  '<tr><td>L2-Amp</td><td align="right">' + d['L2-Amp'] + '</td><td>Amp</td></tr>'
    +  '<tr><td>L3-Amp</td><td align="right">' + d['L3-Amp'] + '</td><td>Amp</td></tr>')
    html_e = '''
            </table>
        </body>
    </html>
    '''
    return html_s + html_r + html_e


try:
    # Open html socket
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
except OSError as ex:
    s.close()
    logging.exception(ex,'Socket exception')
    wlan.disconnect()
    #reset()
    
logging.info('listening on'+ str(addr))

try:
    _thread.start_new_thread(read_data, ())
except:
    sys.exit(1)

# Listen for connections
while True:
    try:
        cl, addr = s.accept()
        t = time.localtime()
        logging.info(f"client connected from {addr} GMT {t[4]}:{t[5]}:{t[6]}")
        cl_file = cl.makefile('rwb', 0)
        while True:
            line = cl_file.readline()
            if not line or line == b'\r\n':
                break
        response = make_html(processdata(get_data()))
        logging.debug(response)
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()
    except KeyboardInterrupt:  # OSError as e:
        STOP = True
        s.close()
        wlan.disconnect()
        sys.exit(1)
    finally:
        logging.info('connection closed')
