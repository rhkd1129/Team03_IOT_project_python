import RPi.GPIO as GPIO
import time

class Laser():
    def __init__(self, sig=None):
        self.__sig = sig
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(sig, GPIO.OUT)

    def on(self):
        GPIO.output(self.__sig, GPIO.LOW)


    def off(self):
        GPIO.output(self.__sig, GPIO.HIGH)



if __name__ == '__main__':
    try:
        laser = Laser(sig = 37)
        while True:
            laser.on()
            time.sleep(0.1)
            # laser.off()
            # time.sleep(0.1)


    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()