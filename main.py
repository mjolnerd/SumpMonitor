import gc

from machine import Pin, ADC
from time import sleep_ms
from time import gmtime
from time import ticks_ms
from time import ticks_add
from time import ticks_diff

try:
  import usocket as socket
except:
  import socket

def gen_html(timestamp, reading):
    html = f'{timestamp},{round(reading,1)}'
    return html

def iso8601():
    year, month, day, hour, mins, secs, weekday, yearday = gmtime()
    return f'{year}-{month:02d}-{day:02}T{hour:02d}:{mins:02d}:{secs:02d}Z'

def main():

    # Oscar lends a hand
    gc.collect()
    gc.enable()

    # Sensor pin setup
    etape = ADC(Pin(36)) #PIN 4 on wESP32 GPIO
    etape.atten(ADC.ATTN_11DB)

    # Reading update cadence (milliseconds)
    sample_delay = 5 * 1000
    sample_tick = ticks_add(ticks_ms(), sample_delay)

    # Create and prime our moving average for etape
    etape_window = 10
    etape_index = 0
    etape_readings = []
    for etape_index in range(0, etape_window):
        etape_readings.append(etape.read())
        print(f'{iso8601()} PRIME ARRAY {etape_index} {etape_readings[etape_index]}')
        sleep_ms(sample_delay)
    print(etape_index)
    print(etape_readings)
    etape_index = (etape_index + 1) % etape_window
    print(etape_index)
    # Open up a port to exfiltrate our sensor data onto the network
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)


    while True:
        if ticks_diff(sample_tick, ticks_ms()) < 0:
            etape_readings[etape_index] = etape.read()
            ### So this loop blocks on s.accept(),  we may need to come up with something
            ###  threaded to make this moving average thing work well.
            #etape_avg = sum(etape_readings) / etape_window
            etape_avg = etape_readings[etape_index]
            print(f'{iso8601()} READING {etape_readings[etape_index]}')
            etape_index = (etape_index + 1) % etape_window
            # Create the new html page
            html_out = gen_html(iso8601(), etape_avg)
            # Set a time to run this again
            sample_tick = ticks_add(ticks_ms(), sample_delay)
            #hose out the stalls
            gc.collect()

        # We have incoming connection, ready the data!
        conn, addr = s.accept()
        print(f'{iso8601()} CONNECT {str(addr)}')
        request = conn.recv(1024)
        request = str(request)
        print(f'{iso8601()} REQUEST {request}')
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(html_out)
        conn.close()

if __name__ == "__main__":
    main()

