# Define feeder control objects with the proper GPIOs, addresses, and other config parameters
from objects.charLCD import CharLCD
from objects.DCMotor import DCMotor
from objects.distanceSensor import DistanceSensor
from objects.camera import Camera
from app.configs.hwCfg import HardwareConfig as hwConfig

class CatFeeder:
    def __init__(self):
        self.stop_threads = False
        self.threads = []
        # Initialize the global variable `initialized` to False.
        self.initialized = False
        # Initialize the hardware objects 
        self.display = None
        self.motor = None
        self.picam = None
        self.foodsens = None
        self.hardwareConfigured = False
        self.hardwareInitialized = {
            "display" : False,
            "motor" : False,
            "picam" : False,
            "foodsens" : False
        }
        self.hardwareEnabled = {
            "display" : False,
            "motor" : False,            
            "picam" : False,
            "foodsens" : False
        }
          
    def setupHardware(self):
        self.hardwareConfigured = True
        exceptions = []
        self.hardwareEnabled["display"] = hwConfig.HW_ENABLE["DISPLAY"]
        self.hardwareEnabled["motor"] = hwConfig.HW_ENABLE["MOTOR"]
        self.hardwareEnabled["picam"] = hwConfig.HW_ENABLE["CAMERA"]
        self.hardwareEnabled["foodsens"] = hwConfig.HW_ENABLE["DSENS"]
        try:
            self.display = CharLCD(address = hwConfig.LCD["LCD_I2C_ADDR"], height = hwConfig.LCD["ROWS"], width = hwConfig.LCD["COLS"])
        except Exception as e:
            exceptions.append(e)
            self.hardwareConfigured = False
            print("Error initializing display. Verify hardware configuration.")
        try:
            self.motor = DCMotor(en_1_pin=hwConfig.GPIOS["DC_MOTOR_EN1"], en_2_pin=hwConfig.GPIOS["DC_MOTOR_EN2"])
        except Exception as e:
            exceptions.append(e)
            self.hardwareConfigured = False
            print("Error initializing motor. Verify hardware configuration.")
        try:
            self.picam = Camera(resolution=hwConfig.CAMERA["RESOLUTION"])
        except Exception as e:
            exceptions.append(e)
            self.hardwareConfigured = False
            print("Error initializing camera. Verify hardware configuration.")
        try:
            self.foodsens = DistanceSensor(trig_pin=hwConfig.GPIOS["DSENS_TRIG"], echo_pin=hwConfig.GPIOS["DSENS_ECHO"])
        except Exception as e:
            exceptions.append(e)
            self.hardwareConfigured = False
            print("Error initializing distance sensor. Verify hardware configuration.")
        if exceptions:
            return False, exceptions
        else:
            return True, None
        
    def initializeDisplay(self):
        if not self.display.initialized:
            try:
                self.display.initialize()
            except Exception as e:
                raise RuntimeError(e)
            
    def initializeMotor(self):
        if not self.motor.initialized:
            try:
                self.motor.initialize()
            except Exception as e:
                raise RuntimeError(e)
            
    def initializeCamera(self):
        if not self.picam.initialized:
            try:
                self.picam.initialize()
            except Exception as e:
                raise RuntimeError(e)
            
    def initializeDistanceSensor(self):
        if not self.foodsens.initialized:
            try:
                self.foodsens.initialize()
            except Exception as e:
                raise RuntimeError(e)
            
    def startCamera(self):
        if self.picam.initialized:
            try:
                self.picam.start()
            except Exception as e:
                raise RuntimeError(e)
        else:
            raise RuntimeError("Camera not initialized.")
        
    def stopCamera(self):
        if self.picam.initialized:
            try:
                self.picam.cleanup()
            except Exception as e:
                raise RuntimeError(e)
            
    def initialize(self):
        if not self.hardwareConfigured:
            success, exceptions = self.setupHardware()
            if not success:
                for exceptions in exceptions:
                    print("Warning, could not configure hardware: " + str(exceptions))
        if not self.hardwareInitialized["display"] and self.hardwareEnabled["display"]:
            self.initializeDisplay()
            self.hardwareInitialized["display"] = True
        if not self.hardwareInitialized["motor"] and self.hardwareEnabled["motor"]:
            self.initializeMotor()
            self.hardwareInitialized["motor"] = True
        if not self.hardwareInitialized["picam"] and self.hardwareEnabled["picam"]:
            self.initializeCamera()
            self.hardwareInitialized["picam"] = True
        if not self.hardwareInitialized["foodsens"] and self.hardwareEnabled["foodsens"]:
            self.initializeDistanceSensor()
            self.hardwareInitialized["foodsens"] = True
                    
        