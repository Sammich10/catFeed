import RPi.GPIO as GPIO
import time
import pigpio

rpi = pigpio.pi()

class DCMotor:
    pin1 = 23
    pin2 = 25
    def __init__(self):
        rpi.set_mode(self.pin1, pigpio.OUTPUT)
        rpi.set_mode(self.pin2, pigpio.OUTPUT)
    def dispense(self,t):
        rpi.write(self.pin1, 1)
        rpi.write(self.pin2, 0)
        time.sleep(t)
        rpi.write(self.pin1,0)
        rpi.write(self.pin2,1)
        time.sleep(.2)
        rpi.write(self.pin2,0)



