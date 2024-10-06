import time
import pigpio

# Define the DCMotor class, which will be used to control the motor
class DCMotor:
    def __init__(self, en_1_pin = 19, en_2_pin = 26):
        self.en1 = en_1_pin
        self.en2 = en_2_pin
        self.initialized = False

    def initialize(self):
        try:
            self.rpi.set_mode(self.en1, pigpio.OUTPUT)
            self.rpi.set_mode(self.en2, pigpio.OUTPUT)
        except Exception as e:
            raise RuntimeError(e)
        self.initialized = True
        
    def forward(self,t):
        self.rpi.write(self.en1, 1)
        self.rpi.write(self.en2, 0)
        time.sleep(t)
        self.rpi.write(self.en1, 0)
        
    def backward(self,t):
        self.rpi.write(self.en1, 0)
        self.rpi.write(self.en2, 1)
        time.sleep(t)
        self.rpi.write(self.en2, 0)
        
    def setup(self):
        self.rpi.write(self.en1, 0)
        self.rpi.write(self.en2, 0)        

    rpi = pigpio.pi()
    