import spidev
import time
import RPi.GPIO as GPIO

spi = spidev.SpiDev()
spi.open(0, 0)  

spi.max_speed_hz = 1000000

LED_PIN = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)


def analog_read(channel):
  ret = spi.xfer2([1, (channel + 8) << 4, 0])
  adc_out = ((ret[1] & 3) << 8) + ret[2]
  return adc_out

try:
    while True:
        reading = analog_read(0)
        if reading < 512:
          GPIO.output(LED_PIN, 1)
        else:
          GPIO.output(LED_PIN, 0)
        voltage = reading * 3.3 / 1023
        print("Reading = %d, voltage = %f" % (reading, voltage))
        time.sleep(0.5)
finally:
    spi.close()
