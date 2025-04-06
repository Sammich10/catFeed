import time
import pigpio

# Define the DCMotor class, which will be used to control the motor
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
            self.rpi.set_mode(self.en1, pigpio.OUTPUT)
            self.rpi.set_mode(self.en2, pigpio.OUTPUT)
        except Exception as e:
            print("Error initializing motor GPIO pins: " + str(e))
            raise e
        self.setup()
        self.initialized = True
        
    def forward(self,t):
        """
        Runs the motor in the forward direction for a specified duration
        
        Args:
            t : float
                The duration to run the motor in seconds
        """
        self.rpi.write(self.en1, 1)
        self.rpi.write(self.en2, 0)
        time.sleep(t)
        self.rpi.write(self.en1, 0)
        
    def backward(self,t):
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
        time.sleep(t)
        self.rpi.write(self.en2, 0)
        
    def setup(self):
        """
        Sets both enable signals (EN1 and EN2) to low
        
        Args:
            None
            
        Returns:
            None
        """
        self.rpi.write(self.en1, 0)
        self.rpi.write(self.en2, 0)        

    rpi = pigpio.pi()
    