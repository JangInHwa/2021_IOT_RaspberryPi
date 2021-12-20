from flask import Flask
import RPi.GPIO as GPIO

RED_LED_PIN = 17
BLUE_LED_PIN = 27

app = Flask(__name__)

GPIO.setmode(GPIO.BCM)
GPIO.setup(RED_LED_PIN, GPIO.OUT)
GPIO.setup(BLUE_LED_PIN, GPIO.OUT)

@app.route('/')
def index():
	return '''
	<p>Hello, Flask!!</p>
	<a href="/red/on">RED LED ON</a>
	<a href="/red/off">RED LED OFF</a>
	<a href="/blue/on">BLUE LED ON</a>
	<a href="/blue/off">BLUE LED OFF</a>
	'''


@app.route('/<color>/<op>')
def led_op(color, op):
	if color == 'red':
		if op == 'on':
			GPIO.output(RED_LED_PIN, GPIO.HIGH)
			return '''
				<p>RED LED ON</p>
				<a href="/">Go Home</a>
				'''
		elif op == 'off':
			GPIO.output(RED_LED_PIN, GPIO.LOW)
			return '''
				<p>RED LED OFF</p>
				<a href="/">Go Home</a>
				'''
	elif color == 'blue':
		if op == 'on':
			GPIO.output(BLUE_LED_PIN, GPIO.HIGH)
			return '''
				<p>BLUE LED ON</p>
				<a href="/">Go Home</a>
				'''
		elif op == 'off':
			GPIO.output(BLUE_LED_PIN, GPIO.LOW)
			return '''
				<p>BLUE LED OFF</p>
				<a href="/">Go Home</a>
				'''


if __name__ == '__main__':
	try:
		app.run(host='0.0.0.0')
	finally:
		GPIO.cleanup()
