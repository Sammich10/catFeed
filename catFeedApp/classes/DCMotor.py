import RPi.GPIO as GPIO
import time
import pigpio

rpi = pigpio.pi()

class DCMotor:
    power_pin = 22
    def __init__(self):
        rpi.set_mode(self.power_pin, pigpio.OUTPUT)
    def forward(self,t):
        rpi.write(self.power_pin, 1)
        time.sleep(t)
        rpi.write(self.power_pin, 0)



