import RPi.GPIO as GPIO
import time
import datetime

GPIO.setmode(GPIO.BCM)

# 문자에 따른 세그먼트의 핀 출력값을 미리 설정해둠
chars = {
    ' ': (0, 0, 0, 0, 0, 0, 0),
    '0': (1, 1, 1, 1, 1, 1, 0),
    '1': (0, 1, 1, 0, 0, 0, 0),
    '2': (1, 1, 0, 1, 1, 0, 1),
    '3': (1, 1, 1, 1, 0, 0, 1),
    '4': (0,  1, 1, 0, 0, 1, 1),
    '5': (1, 0, 1, 1, 0, 1, 1),
    '6': (1, 0, 1, 1, 1, 1, 1),
    '7': (1, 1, 1, 0, 0, 0, 0),
    '8': (1, 1, 1, 1, 1, 1, 1),
    '9': (1, 1, 1, 1, 0, 1, 1),
    '-': (0, 0, 0, 0, 0, 0, 1),
}


# LED를 관리하는 클래스
class LED:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)

    def on(self):
        GPIO.output(self.pin, 1)

    def off(self):
        GPIO.output(self.pin, 0)


# 버튼을 관리하는 클래스
class Button:
    def __init__(self, pin):
        self.pin = pin
        self.onDownListeners = []
        self.onUpListeners = []
        self.before = 0
        GPIO.setup(pin, GPIO.IN, GPIO.PUD_DOWN)

    def addOnDownListener(self, onDown):
        self.onDownListeners.append(onDown)

    def removeOnDownListener(self, onDown):
        if self.onDownListeners.count(onDown):
            self.onDownListeners.remove(onDown)

    def addOnUpListener(self, onUp):
        self.onUpListeners.append(onUp)

    def removeOnUpListener(self, onUp):
        if self.onUpListeners.count(onUp):
            self.onUpListeners.remove(onUp)

    def is_down(self):
        return GPIO.input(self.pin)

    def update(self):
        button_input = GPIO.input(self.pin)
        if (button_input == 1 and self.before == 0):
            for listener in self.onDownListeners:
                listener(self.pin)
        if (button_input == 0 and self.before == 1):
            for listener in self.onUpListeners:
                listener(self.pin)
        self.before = button_input


# 삑 소리 하나를 표현하는 클래스
class Sound:
    def __init__(self):
        self.start = 0
        self.end = 0
        self.frequency = 0


# 부저를 관리하는 클래스
class Buzzer:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(16, GPIO.OUT)
        self.pwm = GPIO.PWM(16, 100)
        self.pwm.start(0)
        self.pwm.ChangeDutyCycle(0)

    def play(self, frequency):
        self.pwm.ChangeDutyCycle(99)
        self.pwm.ChangeFrequency(frequency)

    def stop(self):
        self.pwm.ChangeDutyCycle(0)


# 노래를 관리하는 클래스
class SoundPlayer:
    def __init__(self):
        self.sheet = []
        self.is_playing = False
        self.on_play_music = None
        self.on_stop_music = None

    def setMusic(self, sheet):
        self.sheet = sheet

    def play(self, buzzer):
        self.on_play_music()
        self.is_playing = True
        self.buzzer = buzzer
        self.buzzer.stop()
        self.note_index = 0
        self.start_time = datetime.datetime.now()

    def stop(self):
        self.on_stop_music()
        if self.is_playing:
            self.buzzer.stop()
            self.is_playing = False

    def update(self):
        if self.is_playing:
            recording_timedelta = (datetime.datetime.now() - self.start_time)
            recording_time = recording_timedelta.seconds * 1000000 + recording_timedelta.microseconds
            if recording_time > self.sheet[self.note_index].end:
                self.note_index += 1
                self.buzzer.stop()
                if self.note_index >= len(self.sheet):
                    self.stop()
                    return
            if self.sheet[self.note_index].start <= recording_time:
                self.buzzer.play(self.sheet[self.note_index].frequency)


# 녹음 기능을 담당하는 클래스
class Recorder:
    def __init__(self):
        self.is_recording = False
        self.sheet = []

    def soundStart(self, pin):
        self.sheet.append(Sound())
        recording_timedelta = (datetime.datetime.now() - self.start_time)
        recording_time = recording_timedelta.seconds * 1000000 + recording_timedelta.microseconds
        self.sheet[-1].start = recording_time
        self.sheet[-1].frequency = 523

    def soundEnd(self, pin):
        recording_timedelta = (datetime.datetime.now() - self.start_time)
        recording_time = recording_timedelta.seconds * 1000000 + recording_timedelta.microseconds
        self.sheet[-1].end = recording_time

    def record(self, button: Button):
        self.sheet = []
        self.button = button
        self.button.addOnDownListener(self.soundStart)
        self.button.addOnUpListener(self.soundEnd)
        self.is_recording = True
        self.start_time = datetime.datetime.now()
        if self.button.is_down():
            self.soundStart(None)

    def record_stop(self):
        if self.button.is_down():
            self.soundEnd(None)
        if self.is_recording:
            self.button.removeOnDownListener(self.soundStart)
            self.button.removeOnUpListener(self.soundEnd)
            self.is_recording = False


# 세그먼트를 관리하는 클래스
class Segment:
    def __init__(self, segment_pin, digit_pin):
        self.str = '    '
        self.dot = [0, 0, 0, 0]
        self.segment_pin = segment_pin
        self.digit_pin = digit_pin
        for segment in segment_pin:
            GPIO.setup(segment, GPIO.OUT)
            GPIO.output(segment, 0)
        for digit in digit_pin:
            GPIO.setup(digit, GPIO.OUT)
            GPIO.output(digit, 1)

    def setString(self, str, dot=[0, 0, 0, 0]):
        self.str = str
        self.dot = dot

    def update(self):
        global chars
        for digit in range(4):
            GPIO.output(25, self.dot[digit])
            for loop in range(0, 7):
                GPIO.output(self.segment_pin[loop],
                            chars[self.str[digit]][loop])
            GPIO.output(self.digit_pin[digit], 0)
            time.sleep(0.001)
            GPIO.output(self.digit_pin[digit], 1)


is_playing = False
sheets: list = []
music_index = -1
mode = ''  #'select', 'play', 'record'가 존재함

recorder = Recorder()
beat_button = Button(12)
play_button = Button(13)
record_button = Button(19)
up_button = Button(5)
down_button = Button(6)
buzzer = Buzzer(16)
sound_player = SoundPlayer()
segment = Segment((11, 4, 23, 8, 7, 10, 18, 25), (22, 27, 17, 24))
recording_led = LED(26)
playing_led = LED(20)

# 출력된 버튼이 무슨 버튼인지를 출력
# def buttonClick(pin):
#     button_name = {
#         12: 'beat_button',
#         5: 'up_button',
#         6: 'down_button',
#         13: 'play_button',
#         19: 'record_button'
#     }
#     print(button_name[pin] + 'clicked')


# 음악 재생
def play_music(_):
    global buzzer
    global sheets
    global music_index
    if mode == 'select' and music_index != -1:
        print('play No.' + str(music_index))
        sound_player.setMusic(sheets[music_index])
        sound_player.play(buzzer)
    elif mode == 'play':
        print('stop playing No.' + str(music_index))
        sound_player.stop()


# up 버튼 클릭
def up_button_click(pin):
    global music_index
    global mode
    global segment
    if mode == 'select' and music_index != -1:
        music_index += 1
        if music_index >= len(sheets):
            music_index = 0
        segment.setString(str(music_index).zfill(4))


#down 버튼 클릭
def down_button_click(pin):
    global music_index
    global mode
    if mode == 'select' and music_index != -1:
        music_index -= 1
        if music_index < 0:
            music_index = len(sheets) - 1
        segment.setString(str(music_index).zfill(4))


# 모드를 설정
def set_mode(mode_str):
    global mode
    mode = mode_str


# 음악을 녹음
def record_music(_):
    global sheets
    global mode
    global recording_led
    global music_index
    global segment
    global recorder
    if mode == 'select':  #'select'모드에서만 레코드를 할 수 있음
        print('Recording No.' + str(len(sheets)) + ' started')
        set_mode('record')
        segment.setString('    ')
        recording_led.on()
        recorder.record(beat_button)
    else:
        set_mode('select')
        recorder.record_stop()
        recording_led.off()
        if len(recorder.sheet) == 0:
            print('Nothing Recorded!')
            if len(sheets) == 0:
                segment.setString('----')
            return
        print('No.' + str(len(sheets)) + ' recorded successfully!')
        sheets.append(recorder.sheet)
        music_index = len(sheets) - 1
        segment.setString(str(music_index).zfill(4))


# 부저를 켬
def buzzOn(_):
    global buzzer
    if mode != 'play':
        buzzer.play(523)


# 부저를 끔
def buzzOff(_):
    global buzzer
    if mode != 'play':
        buzzer.stop()


# 재생 시작
def play_start():
    global playing_led
    set_mode('play')
    playing_led.on()


#재생 중단
def play_stop():
    global playing_led
    set_mode('select')
    playing_led.off()


#초기 설정을 해주는 함수, 단 한번 실행됨
def setup():
    global beat_button
    global play_button
    global record_button
    global up_button
    global down_button
    global sound_player
    global segment
    # beat_button.addOnDownListener(buttonClick)
    # play_button.addOnDownListener(buttonClick)
    # record_button.addOnDownListener(buttonClick)
    # up_button.addOnDownListener(buttonClick)
    # down_button.addOnDownListener(buttonClick)
    beat_button.addOnDownListener(buzzOn)
    beat_button.addOnUpListener(buzzOff)
    play_button.addOnDownListener(play_music)
    record_button.addOnDownListener(record_music)
    up_button.addOnDownListener(up_button_click)
    down_button.addOnDownListener(down_button_click)
    sound_player.on_play_music = play_start
    sound_player.on_stop_music = play_stop
    set_mode('select')
    segment.setString('----')


# 업데이트 함수, 프로그램 실행 중에 계속 반복됨
def update():
    global beat_button
    global play_button
    global record_button
    global up_button
    global down_button
    global sound_player
    global segment
    beat_button.update()
    play_button.update()
    record_button.update()
    up_button.update()
    down_button.update()
    sound_player.update()
    segment.update()


setup()

# 무한루프로 반복
try:
    while True:
        update()
finally:
    GPIO.cleanup()
