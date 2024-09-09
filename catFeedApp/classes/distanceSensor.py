import time
import threading
import pigpio

class DistanceSensor:
    def __init__(self, trig_pin=16, echo_pin=20):
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.pi = pigpio.pi()
        self.done = threading.Event()
        self.low = 0

    def _rise(self, gpio, level, tick):
        self.high = tick

    def _fall(self, gpio, level, tick):
        self.low = tick - self.high
        self.done.set()

    def _read_distance_mm(self):
        self.done.clear()
        self.pi.gpio_trigger(self.trig_pin, 50, 1)
        if self.done.wait(timeout=5):
            return self.low / 58.0 / 100.0 * self.METERS_TO_MM
        return -1
    
    def setFull_mm(self, mm):
        self.MAX_DISTANCE = mm
        
    def setEmpty_mm(self, mm):
        self.MIN_DISTANCE = mm
        
    def calibrate_max(self):
        sum = 0
        for i in range(3):
            sum += self._read_distance_mm()
            time.sleep(0.5)
        self.MAX_DISTANCE = sum/3
        
    def calibrate_min(self):
        sum = 0
        for i in range(3):
            sum += self._read_distance_mm()
            time.sleep(0.5)
        self.MIN_DISTANCE = sum/3
        
    def getReading_mm(self, samples=1):
        sum = 0 
        readings = []
        for i in range(samples):
            dist = self._read_distance_mm()
            # Accumulate the distance readings
            sum+=dist
            # Add the readings to the list
            readings.append(dist)
            time.sleep(self.R_DELAY)
            
        avg = sum/samples
        # Return the average
        return avg
    
    def getReading_percent(self, samples=1):
        percent = self.getReading_mm(samples) / self.MAX_DISTANCE * 100
        if percent > 100:
            percent = 100
            
        return percent


    # Setup the trigger and echo pins with the pigpio library
    def setup(self):
        # The trigger pin is an output, it is used to send the ultrasonic pulse
        self.pi.set_mode(self.trig_pin, pigpio.OUTPUT)
        # The echo pin is an input, it is used to measure the distance, measuring the ticks
        # when the echo pin goes high and low
        self.pi.set_mode(self.echo_pin, pigpio.INPUT)
        self.pi.callback(self.echo_pin, pigpio.RISING_EDGE, self._rise)
        self.pi.callback(self.echo_pin, pigpio.FALLING_EDGE, self._fall)

    MAX_DISTANCE = 150
    MIN_DISTANCE = 0
    METERS_TO_MM = 1000 
    R_DELAY = 0.01      # 10ms


