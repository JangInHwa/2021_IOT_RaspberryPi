import RPi.GPIO as GPIO
import cv2
import string
import random

#gpio 설정
GPIO.setmode(GPIO.BCM)

#버튼 클래스
class Button:
	def __init__(self, pin):
		self.pin = pin
		self.on_down = []
		self.on_up = []
		self.before = 1
		GPIO.setup(self.pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
	
	#버튼 상태의 변화를 감지해 이벤트를 발생시킴
	def update(self):
		val = GPIO.input(self.pin)
		if val != self.before:
			if val == 0:
				for function in self.on_down:
					function(self.pin)
			else:
				for function in self.on_up:
					function(self.pin)
			self.before = val

#릴레이 클래스
class Relay:
	def __init__(self, pin):
		self.pin = pin
		GPIO.setup(self.pin, GPIO.OUT)


	#릴레이 on
	def on(self):
		GPIO.output(self.pin, 1)

	#릴레이 off
	def off(self):
		GPIO.output(self.pin, 0)

#팬 클래스
class Fan:
	def __init__(self, in1, in2, en) -> None:
		self.in1 = in1
		self.in2 = in2
		self.en = en
		GPIO.setup(self.in1, GPIO.OUT)
		GPIO.setup(self.in2, GPIO.OUT)
		GPIO.setup(self.en, GPIO.OUT)
		GPIO.output(self.in1, GPIO.LOW)
		GPIO.output(self.in2, GPIO.LOW)
		self.p = GPIO.PWM(en, 1000)
		self.p.start(25)
	
	def on(self):
		GPIO.output(self.in1, GPIO.HIGH)
		GPIO.output(self.in2, GPIO.LOW)
	
	def off(self):
		GPIO.output(self.in1, GPIO.LOW)
		GPIO.output(self.in2, GPIO.LOW)

#필터 클래스
class Snow:
	def __init__(self) -> None:
		self.filter_image = None
		self.cam = cv2.VideoCapture(0)
		if not self.cam.isOpened():
			print('Camera open failed')
			exit()

		self.face_cascade = cv2.CascadeClassifier('./xml/face.xml')

		self.cam_width  = self.cam.get(3)  # float `width`
		self.cam_height = self.cam.get(4)

	#소멸자, 캠을 정리함
	def __del__(self):
		self.cam.release()
	
	#필터 이미지를 설정함
	def set_filter_image(self, path:str):
		if path == None:
			self.filter_image = None
		else:
			self.filter_image = cv2.imread(path)


	#사진을 찍어 파일에 저장
	def save_to_file(self, path):
		ret, frame = self.cam.read()
		if not ret:
			return
		
		if type(self.filter_image) != type(None):
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

			for (x, y, w, h) in faces:
				self.add_filter(frame, self.filter_image, x, y, w, h)
		print(f'saved to {path}')
		cv2.imwrite(path, frame)
		

	#원본 이미지에 필터 이미지를 씌워줌
	def add_filter(self, original_img, filter_img, x, y, w, h):
		rows, cols, channels = filter_img.shape
		width_ratio, height_ratio = w / rows, h / cols
		max_ratio = max(width_ratio, height_ratio)
		resized_width, resized_height = cols * max_ratio, rows * max_ratio
		roi_x, roi_y =  x- (resized_width - w)//2, y - (resized_height - h)//2
		if roi_x < 0:
			resized_width += roi_x
			roi_x = 0
		if roi_x + resized_width > self.cam_width:
			resized_width -= roi_x + resized_width - self.cam_width
		if roi_y < 0:
			resized_height += roi_y
			roi_y = 0
		if roi_y + resized_height > self.cam_height:
			resized_height -= roi_y + resized_height - self.cam_height
		resized_width, resized_height = int(resized_width), int(resized_height)
		roi_x, roi_y = int(roi_x), int(roi_y)
		resized_animal_filter_img = cv2.resize(self.filter_image, dsize=(resized_width, resized_height), interpolation=cv2.INTER_NEAREST)
		ret, mask = cv2.threshold(resized_animal_filter_img[:, :, 2], 0, 255, cv2.THRESH_BINARY)
		mask_inv = cv2.bitwise_not(mask)
		roi = original_img[roi_y:roi_y+resized_height, roi_x:roi_x+resized_width]
		dst = cv2.add(cv2.bitwise_and(roi, roi, mask=mask_inv), resized_animal_filter_img)
		original_img[roi_y:roi_y+resized_height, roi_x:roi_x+resized_width] = dst

	#카메라에서 프레임을 받아와 얼굴을 컴출한 후 필터를 씌워 윈도우에 띄워줌
	def update(self):
		ret, frame = self.cam.read()
		if not ret:
			return
		
		if type(self.filter_image) != type(None):
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

			for (x, y, w, h) in faces:
				self.add_filter(frame, self.filter_image, x, y, w, h)

		cv2.imshow('frame', frame)

		if cv2.waitKey(10) == 13:
			exit()

#업데이트 될 엘레멘트의 목록을 담는 큐
update_queue = []

light = Relay(17)
is_light_on = True

#버튼들을 선언
red_button = Button(26)
yellow_button = Button(19)
blue_button = Button(13)
black_button = Button(6)
white_button = Button(5)
fan_button = Button(20)
light_button = Button(16)

#버튼들을 update_queue에 등록
update_queue.append(red_button)
update_queue.append(yellow_button)
update_queue.append(blue_button)
update_queue.append(black_button)
update_queue.append(white_button)
update_queue.append(fan_button)
update_queue.append(light_button)

#snow 객체 생성, update_queue에 등록
snow = Snow()
update_queue.append(snow)

#fan 객체 생성
fan = Fan(24, 23, 25)
is_fan_on = False

#버튼의 핀번호를 출력
def print_button(pin):
	print(pin)

#필터를 없앰
def set_filter_none(pin):
	global snow
	snow.set_filter_image(None)

#필터를 라쿤으로 설정
def set_filter_racoon(pin):
	global snow
	snow.set_filter_image('assets/racoon.png')

#필터를 당근으로 설정
def set_filter_carrot(pin):
	global snow
	snow.set_filter_image('assets/carrot.png')

#필터를 코알라로 설정
def set_filter_koala(pin):
	global snow
	snow.set_filter_image('assets/koala.png')

#필터를 곰으로 설정
def set_filter_bear(pin):
	global snow
	snow.set_filter_image('assets/bear.png')


#조명 on,off
def light_on_off(pin):
	global is_light_on
	global light
	if is_light_on:
		light.off()
	else:
		light.on()
	is_light_on = not is_light_on

#랟덤 파일명 생성
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

#사진 찍기
def take_picture(pin):
	global snow
	snow.save_to_file('static/images/' + id_generator(6) + '.png')

#fan on, off
def fan_on_off(pin):
	global is_fan_on
	global Fan
	if is_fan_on:
		fan.off()
	else:
		fan.on()
	is_fan_on = not is_fan_on

#버튼 클래스에 on_down 이벤트로 print_button 등록
red_button.on_down.append(print_button)
yellow_button.on_down.append(print_button)
blue_button.on_down.append(print_button)
black_button.on_down.append(print_button)
white_button.on_down.append(print_button)
fan_button.on_down.append(print_button)
light_button.on_down.append(print_button)

red_button.on_down.append(set_filter_racoon)
yellow_button.on_down.append(set_filter_carrot)
blue_button.on_down.append(set_filter_koala)
black_button.on_down.append(set_filter_none)
white_button.on_down.append(take_picture)
light_button.on_down.append(light_on_off)
fan_button.on_down.append(fan_on_off)

light_on_off(None)

#update 함수, update_queue에 등록된 각 엘레멘트들의 상태를 주기적으로 업데이트 해줌
#이벤트를 발생시키고 윈도우를 업데이트 함
def update():
	for element in update_queue:
		element.update()
	

if __name__ == '__main__':
	try:
		while True: #update 함수를 계속 반복 실행함
			update()
	finally:
		cv2.destroyAllWindows() #cv2 정리
		GPIO.cleanup() #gpio 정리
