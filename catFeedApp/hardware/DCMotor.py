"""
This module is used to control the DC motor using the Raspberry Pi's GPIO pins
"""

# Import the pigpio library for GPIO control
import pigpio
# Import sleep for delay
from time import sleep

class DCMotor:
    def __init__(self, en_1_pin = 19, en_2_pin = 26):
        """
        Initializes the DCMotor object with the specified GPIO pins
        
        Args:
            en_1_pin : int
                The GPIO pin for the first enable signal (EN1)
            en_2_pin : int
                The GPIO pin for the second enable signal (EN2)
            
        Returns:
            None
        """
        self.en1 = en_1_pin
        self.en2 = en_2_pin
        self.rpi = pigpio.pi()
        self.initialized = False

    def initialize(self):
        """
        Initializes the GPIO pins for the motor and sets up the motor.
        
        Args:
            None
            
        Returns:
            None
            
        Raises:
            RuntimeError if the GPIO pins cannot be set to output mode.
        """
        try:
            # Initialize the GPIO pins as outputs
            self.rpi.set_mode(self.en1, pigpio.OUTPUT)
            self.rpi.set_mode(self.en2, pigpio.OUTPUT)
            # Set both enable signals (EN1 and EN2) to low
            self.rpi.write(self.en1, 0)
            self.rpi.write(self.en2, 0)  
        except Exception as e:
            print("Error initializing motor GPIO pins: " + str(e))
            raise e
        self.initialized = True
        
    def _forward(self,t):
        """
        Runs the motor in the forward direction for a specified duration
        
        Args:
            t : float
                The duration to run the motor in seconds
        """
        self.rpi.write(self.en1, 1)
        self.rpi.write(self.en2, 0)
        sleep(t)
        self.rpi.write(self.en1, 0)
        
    def _backward(self,t):
        """
        Runs the motor in the backward direction for a specified duration

        Args:
            t : float
                The time in seconds for which the motor should run in the backward direction

        Returns:
            None
        """
        self.rpi.write(self.en1, 0)
        self.rpi.write(self.en2, 1)
        sleep(t)
        self.rpi.write(self.en2, 0)              

    