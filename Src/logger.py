from machine import UART, Pin
import time
import _thread
import network
import socket
import sys
import struct
import ubinascii
import logging
import wlan

#log = logging.getLogger("logger","logger.log")
log = logging.getLogger("logger")
log.setLevel(logging.INFO)

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

          while serial.any() == 0:
              time.sleep_ms(10)
              
          baton.acquire()
          lgt = serial.readinto(data)
          baton.release()

          time.sleep_ms(100)
          if STOP: return
      return
     
def get_data():
    try:
        baton.acquire()
        data_str = str(data,"utf-8")
        log.debug(data_str)
        baton.release()
        data_lst = data_str.splitlines()
        return data_lst
    except Excepion as err:
        log.exception(err,"exception in get_data")
        return None

def processdata(lijst):
    meting = {
        'Now': 'fake!',
        'Grid': '11',
        'Day': '8',
        '7-days': '50',
        '30-days': '200',
        '365-days': '2500',
        'Total':'14000',
        'L1-Volt' : '230',
        'L2-Volt' : '230',
        'L3-Volt' : '230',
        'L1-Amp' : '1.0',
        'L2-Amp' : '1.0',
        'L3-Amp' : '1.0'
    }
    if lijst != None and len(lijst) >= 13:
      for value in lijst:
        if value.startswith('1-0:16.7.0'):
            meting['Now'] = value.split('(')[1].split('*')[0]
        elif value.startswith('1-0:2.8.0'):
            meting['Grid'] = value.split('(')[1].split('*')[0]
        elif value.startswith('1-0:1.8.0*96'):
            meting['Day'] = value.split('(')[1].split('*')[0]
        elif value.startswith('1-0:1.8.0*97'):
            meting['7-days'] = value.split('(')[1].split('*')[0]
        elif value.startswith('1-0:1.8.0*98'):
            meting['30-days'] = value.split('(')[1].split('*')[0]
        elif value.startswith('1-0:1.8.0*99'):
            meting['365-days'] = value.split('(')[1].split('*')[0]
        elif value.startswith('1-0:1.8.0*100'):
            meting['Total'] = value.split('(')[1].split('*')[0]
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
               meting[key] = meting[key].lstrip('0')
            if meting[key].find('-')>=0:
               meting[key] = '-' + meting[key][1:].lstrip('0')
            #"""
            if key == "Grid":
                hs = meting["Grid"]
                pp = hs.rfind('.') 
                if pp > 0:
                  meting["Grid"]= hs[:pp+2] # round to 1 decimal
            #"""
    return meting


def show_meting(meting):
    for value in meting:
        w = meting[value].split('*')
        log.info(f'{value}\t{float(w[0]):{7}.{1}f} {w[1]}')


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
        <title>Logarex Power Meter</title>
        </head>
        <body><h1>Logarex Power Meter</h1>
            <table>
            <tr><th align="left">Period</th><th align="right">Use</th><th align="left">Unit</th></tr>
    '''
    html_r = ('<tr><td>Now</td><td align="right">' + d['Now'] + '</td><td>Watt</td></tr>'
    +  '<tr><td>Grid</td><td align="right">' + d['Grid'] + '</td><td>kWh</td></tr>'
    +  '<tr><td>Day</td><td align="right">' + d['Day'] + '</td><td>kWh</td></tr>'
    +  '<tr><td>7--days</td><td align="right">' + d['7-days'] + '</td><td>kWh</td></tr>'
    +  '<tr><td>30-days</td><td align="right">' + d['30-days'] + '</td><td>kWh</td></tr>'
    +  '<tr><td>365days</td><td align="right">' + d['365-days'] + '</td><td>kWh</td></tr>'
    +  '<tr><td>Total</td><td align="right">' + d['Total'] + '</td><td>kWh</td></tr>'
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
    # Open socket
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
except OSError as ex:
    s.close()
    log.exception(ex,'Socket exception')
    wlan.disconnect()
    #machine.soft_reset()
    raise SystemExit
    
log.info('listening on'+ str(addr))

try:
    reader = _thread.start_new_thread(read_data, ())
    log.info('Reader thread started')
except:
    log.info('Reading thread did not start')
    raise SystemExit

# Listen for connections
while True:
    log.info("HTML-Server while loop started")
    try:
        log.info("waiting for a client")
        cl, addr = s.accept()
        t = time.localtime()
        log.info(f"client connected from {addr} GMT {t[3]}:{t[4]}:{t[5]}")
        cl_file = cl.makefile('rwb', 0)
        while True:
            line = cl_file.readline()
            if not line or line == b'\r\n':
                 break
        meting = processdata(get_data())
        response = make_html(meting)
        log.debug(response)
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()
    except KeyboardInterrupt:  # OSError as e:
        STOP = True
        reader.exit()
        cl.close()
        wlan.disconnect()
        sys.exit(1)
    except UnicodeError as ex:
        log.exception(ex,"UnicodeError in socket-loop")
    except OSError as ex:
        log.exception(ex,"OSError")
        #raise SystemExit
    except Exception as ex:
        log.exception(ex,"Exception in socket-loop")
    except BaseException as ex:
        log.exception(ex,"Error in socket-loop")
    finally:
        cl.close()
        log.info('connection closed')
