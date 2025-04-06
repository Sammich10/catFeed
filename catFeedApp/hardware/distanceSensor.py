import time
import threading
import pigpio

class DistanceSensor:
    def __init__(self, trig_pin=16, echo_pin=20):
        """
        Initializes a DistanceSensor object with the specified GPIO pins for the trigger and echo

        Args:
            trig_pin (int): The GPIO pin for the trigger signal (default: 16)
            echo_pin (int): The GPIO pin for the echo signal (default: 20)

        Returns:
            None
        """
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.initialized = False
        self.low = 0

    def _rise(self, tick):
        """
        Callback function for the pigpio library, called when the echo pin rises

        Args:
            gpio (int): The GPIO pin that triggered the callback
            level (int): The level of the GPIO pin that triggered the callback
            tick (int): The number of microseconds since boot that the callback was triggered

        Returns:
            None
        """
        self.high = tick

    def _fall(self, tick):
        """
        Callback function for the pigpio library, called when the echo pin falls

        Args:
            gpio (int): The GPIO pin that triggered the callback
            level (int): The level of the GPIO pin that triggered the callback
            tick (int): The number of microseconds since boot that the callback was triggered

        Returns:
            None
        """
        self.low = tick - self.high
        self.done.set()

    def _read_distance_mm(self):
        """
        Trigger a single measurement of the distance sensor and return the distance in mm

        This function blocks until the measurement is complete or a timeout occurs

        Returns:
            float: The measured distance in mm, or -1 if a timeout occurred
        """
        self.done.clear()
        self.pi.gpio_trigger(self.trig_pin, 50, 1)
        if self.done.wait(timeout=5):
            return self.low / 58.0 / 100.0 * self.METERS_TO_MM
        return -1
    
    def setFull_mm(self, mm):
        """
        Sets the full distance sensor reading in mm

        Args:
            mm (int): The full distance reading in mm
        """
        self.MAX_DISTANCE = mm
        
    def setEmpty_mm(self, mm):
        """
        Sets the empty distance sensor reading in mm

        Args:
            mm (int): The empty distance reading in mm
        """
        self.MIN_DISTANCE = mm
        
    def getReading_mm(self, samples=1):
        """
        Get the average distance reading in mm over a specified number of samples.

        This function takes the specified number of distance readings, averages them,
        and returns the result.

        Args:
            samples (int): The number of distance readings to take. Defaults to 1.

        Returns:
            float: The average distance reading in mm.
        """

        sum = 0 
        readings = []
        for i in range(samples):
            dist = self._read_distance_mm()
            # Accumulate the distance readings
            sum+=dist
            # Add the readings to the list
            readings.append(dist)
            time.sleep(self.R_DELAY*2)
        avg = sum/samples
        # Return the average
        return avg
    
    def getReading_percent(self, samples=1):
        """
        Get the average distance reading in percent over a specified number of samples.

        This function takes the specified number of distance readings, averages them,
        and returns the result as a percentage.

        Args:
            samples (int): The number of distance readings to take. Defaults to 1.

        Returns:
            float: The average distance reading as a percentage.
        """

        percent = (self.MAX_DISTANCE -self.getReading_mm(samples)) / self.MAX_DISTANCE * 100
        if percent > 100:
            percent = 100
        elif percent < 0:
            percent = 0
        else:
            percent = round(percent, 0)     
        return percent


    # Setup the trigger and echo pins with the pigpio library
    def initialize(self):
        """
        Initializes the distance sensor.

        This function sets up the trigger and echo pins using the pigpio library and
        configures the callbacks for the rising and falling edges of the echo pin.

        Args:
            None

        Returns:
            None

        Raises:
            RuntimeError if the pigpio library cannot be initialized or if the
            callback functions cannot be set.
        """
        try:
            self.pi = pigpio.pi()
            self.done = threading.Event()
            # The trigger pin is an output, it is used to send the ultrasonic pulse
            self.pi.set_mode(self.trig_pin, pigpio.OUTPUT)
            # The echo pin is an input, it is used to measure the distance, measuring the ticks
            # when the echo pin goes high and low
            self.pi.set_mode(self.echo_pin, pigpio.INPUT)
            self.pi.callback(self.echo_pin, pigpio.RISING_EDGE, self._rise)
            self.pi.callback(self.echo_pin, pigpio.FALLING_EDGE, self._fall)
        except Exception as e:
            raise RuntimeError(e)
        self.initialized = True

    MAX_DISTANCE = 150
    MIN_DISTANCE = 0
    METERS_TO_MM = 1000 
    R_DELAY = 0.01
    CAL_MEASUREMENTS = 3
    CAL_MEASUREMENT_TIMEOUT_SECONDS = 1


