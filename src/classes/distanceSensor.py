import time
import threading
import pigpio
class DistanceSensor:

    TRIG = 17           # pin connected to the Trig pin of the sonar
    ECHO = 27           # pin connected to the Echo pin of the sonar
    pi = pigpio.pi()
    done = threading.Event()
    hopper_depth = 10   # Hopper depth in cm

    def __init__(self):
        pi.set_mode(TRIG, pigpio.OUTPUT)
        pi.set_mode(ECHO, pigpio.INPUT)
        pi.callback(ECHO, pigpio.RISING_EDGE, rise)
        pi.callback(ECHO, pigpio.FALLING_EDGE, fall)
      
    def rise(self, gpio, level, tick):
        global high
        high = tick

    def fall(self, gpio, level, tick):
        global low
        low = tick - high
        done.set()

    def read_distance(self):
        global low
        done.clear()
        pi.gpio_trigger(TRIG, 50, 1)
        if done.wait(timeout=5):
            return low / 58.0 / 100.0
    
   def calibrate(self, samps):
        x = read_distance()
        average = x
        for i in range(samps):
            average = average + read_distance()
            time.sleep(5)
        hopper_depth = average / samps
        return hopper_depth
    
    def measureFoodRemaining(self):
        x = read_distance()
        return x / hopper_depth
