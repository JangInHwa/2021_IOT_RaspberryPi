from lcd import drivers
import time
import datetime

display = drivers.Lcd()
PIN = 4


try:
	while True:
		display.lcd_display_string('Hello', 2)
		display.lcd_display_string('world', 1)
		time.sleep(1)
finally:
	print('Cleaning up!')
	display.lcd_clear()
