import RPi.GPIO as GPIO
import time
import threading

class Button(threading.Thread):
	def __init__(self, channel=None):
		self.__channel = channel
		GPIO.setmode(GPIO.BOARD)
		GPIO.setwarnings(False)
		GPIO.setup(channel, GPIO.IN)
		self.handler = None
		self.prevState = GPIO.HIGH
		super().__init__(daemon=True)
		self.start()

	def run(self):
		while True:
			currState = GPIO.input(self.__channel)
			if currState != self.prevState:
				if self.handler is not None:
					self.handler(currState)
				self.prevState = currState
			time.sleep(0.5)

########################## testddd ###############################

def handler1(state):
	if state == GPIO.HIGH:
		print("button1: HIGH")
	else:
		print("button1: LOW")

def handler2(state):
    if state == GPIO.HIGH:
        print("button2: HIGH")
    else:
        print("button2: LOW")

if __name__ == "__main__":
	GPIO.setmode(GPIO.BOARD)
	GPIO.cleanup()
	
	button1 = Button(11)
	button2 = Button(12)

	button1.handler = handler1
	button2.handler = handler2
	time.sleep(1000)
