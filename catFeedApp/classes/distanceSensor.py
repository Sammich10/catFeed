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

    def rise(self, gpio, level, tick):
        self.high = tick

    def fall(self, gpio, level, tick):
        self.low = tick - self.high
        self.done.set()

    def read_distance_mm(self):
        self.done.clear()
        self.pi.gpio_trigger(self.trig_pin, 50, 1)
        if self.done.wait(timeout=5):
            return self.low / 58.0 / 100.0 * self.METERS_TO_MM

        return -1

    def setup(self):
        self.pi.set_mode(self.trig_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.echo_pin, pigpio.INPUT)
        self.pi.callback(self.echo_pin, pigpio.RISING_EDGE, self.rise)
        self.pi.callback(self.echo_pin, pigpio.FALLING_EDGE, self.fall)
        
    MAX_DISTANCE = 14
    MIN_DISTANCE = 0
    METERS_TO_MM = 1000


