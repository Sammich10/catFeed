import time
import pigpio

# Define the DCMotor class, which will be used to control the motor
class DCMotor:
    def __init__(self, power_pin = 22):
        self.power_pin = power_pin
        self.rpi.set_mode(self.power_pin, pigpio.OUTPUT)
    def forward(self,t):
        self.rpi.write(self.power_pin, 1)
        time.sleep(t)
        self.rpi.write(self.power_pin, 0)

    rpi = pigpio.pi()
    


