import gc

from machine import Pin, ADC
from time import sleep
from time import gmtime
from time import ticks_ms
from time import ticks_add
from time import ticks_diff

try:
  import usocket as socket
except:
  import socket

def sample_etape():
    etape = ADC(Pin(36)) #PIN 4 on wESP32 GPIO
    etape.atten(ADC.ATTN_11DB)

    # Average several readings over a given period
    sample_period = 1 # seconds
    sample_quantity = 10
    sample_delay = sample_period / sample_quantity
    samples = []
    # Gather samples
    for x in range(sample_quantity):
        samples.append(etape.read())
        sleep(sample_delay)

    #Average samples
    avg = sum(samples) / len(samples)
    return avg

    #rough convert
    #  5cm 2544
    # 60cm 3670
    #ratio = (60 - 5) / (3670 - 2544)
    #cm_maybe = avg * ratio - 114
    #return (cm_maybe, avg, ratio)

def gen_html(timestamp, reading):
    #html = f'<!DOCTYPE html><html><body><p>{timestamp},{round(reading,1)}</p></body></html>'
    html = f'{timestamp},{round(reading,1)}'
    return html

def iso8601():
    year, month, day, hour, mins, secs, weekday, yearday = gmtime()
    return f'{year}-{month:02d}-{day:02}T{hour:02d}:{mins:02d}:{secs:02d}Z'

def main():

    gc.collect()
    gc.enable()

    # Reading update cadence (milliseconds)
    sample_delay = 20 * 1000
    sample_tick = ticks_add(ticks_ms(), sample_delay)
    #get an initial sample
    this_reading = sample_etape()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)


    while True:
        if ticks_diff(sample_tick, ticks_ms()) < 0:
            this_reading = sample_etape()
            print(f'{iso8601()} READING {this_reading}')
            #hose out the stalls
            gc.collect()

        conn, addr = s.accept()
        print(f'{iso8601()} CONNECT {str(addr)}')
        request = conn.recv(1024)
        request = str(request)
        print(f'{iso8601()} REQUEST {request}')
        timestamp = iso8601()
        html_out = gen_html(timestamp, this_reading)
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(html_out)
        conn.close()

if __name__ == "__main__":
    main()

