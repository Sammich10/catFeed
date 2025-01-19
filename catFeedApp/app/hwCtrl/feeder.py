# Define feeder control objects with the proper GPIOs, addresses, and other config parameters
from objects.charLCD import CharLCD
from objects.DCMotor import DCMotor
from objects.distanceSensor import DistanceSensor
from objects.camera import Camera
from app.configs.hwCfg import HardwareConfig

class CatFeeder:
    def __init__(self, hwConfig: object[HardwareConfig]):
        """
        Initialize the CatFeeder class and its hardware objects to the 'uninitialized' state
        
        Args:
            None
        
        Returns:
            None
        """
        
        # Initialize the hardware objects to None
        self.display = None
        self.motor = None
        self.picam = None
        self.foodsens = None
        
        # Initialize the hardware configuration object
        self.config = hwConfig
        
        # Variable flag `hardwareConfigured` to False on class instantiation to signal that the feeder has not run the setupHardware() method
        self.hardwareConfigured = False
        self.hardwareInitialized = {
            "display" : False,
            "motor" : False,
            "picam" : False,
            "foodsens" : False
        }
        self.hardwareEnabled = {
            "display" : self.config.HW_ENABLE["DISPLAY"],
            "motor" : self.config.HW_ENABLE["MOTOR"],            
            "picam" : self.config.HW_ENABLE["CAMERA"],
            "foodsens" : self.config.HW_ENABLE["DSENS"]
        }
          
    def setupHardware(self):
        """
        Initializes the enabled hardware objects with the proper configuration parameters
        
        Args:
            None
            
        Returns:
            True and None if the enabled hardware objects were successfully initialized, False with a list of exceptions if they were not
        """
        exceptions = []
        if self.hardwareEnabled["display"]:
            try:
                self.display = CharLCD(address = self.config.LCD["LCD_I2C_ADDR"], height = self.config.LCD["ROWS"], width = self.config.LCD["COLS"])
            except Exception as e:
                exceptions.append(e)
                print("Error initializing display. Verify hardware configuration.")
        else: 
            print("Display hardware not enabled.")
        if self.hardwareEnabled["motor"]:
            try:
                self.motor = DCMotor(en_1_pin=self.config.GPIOS["DC_MOTOR_EN1"], en_2_pin=self.config.GPIOS["DC_MOTOR_EN2"])
            except Exception as e:
                exceptions.append(e)
                print("Error initializing motor. Verify hardware configuration.")
        else:
            print("Motor hardware not enabled.")
        if self.hardwareEnabled["picam"]:
            try:
                self.picam = Camera(resolution=self.config.CAMERA["RESOLUTION"])
            except Exception as e:
                exceptions.append(e)
                print("Error initializing camera. Verify hardware configuration.")
        else:
            print("Camera hardware not enabled.")
        if self.hardwareEnabled["foodsens"]:
            try:
                self.foodsens = DistanceSensor(trig_pin=self.config.GPIOS["DSENS_TRIG"], echo_pin=self.config.GPIOS["DSENS_ECHO"])
            except Exception as e:
                exceptions.append(e)
                print("Error initializing distance sensor. Verify hardware configuration.")
        else:
            print("Distance sensor hardware not enabled.")
        if exceptions:
            return False, exceptions
        else:
            self.hardwareConfigured = True
            return True, None
        
    def _initializeDisplay(self):
        """
        Run the initialize() method for the display object
        
        Args:
            None
            
        Returns:
            None
            
        Raises:
            RuntimeError if the display object is not initialized properly
        """
        if not self.display.initialized:
            try:
                self.display.initialize()
            except Exception as e:
                raise RuntimeError(e)
            
    def _initializeMotor(self):
        """
        Run the initialize() method for the motor object
        
        Args:         
            None
            
        Returns:
            None
            
        Raises:
            RuntimeError if the motor object is not initialized properly
        """
        if not self.motor.initialized:
            try:
                self.motor.initialize()
            except Exception as e:
                raise RuntimeError(e)
            
    def _initializeCamera(self):
        """
        Run the initialize() method for the camera object
        
        Args:         
            None
            
        Returns:
            None
            
        Raises:
            RuntimeError if the camera object is not initialized properly
        """
        if not self.picam.initialized:
            try:
                self.picam.initialize()
            except Exception as e:
                raise RuntimeError(e)
            
    def _initializeDistanceSensor(self):
        """
        Run the initialize() method for the distance sensor object
        
        Args:         
            None
            
        Returns:
            None
            
        Raises:
            RuntimeError if the distance sensor object is not initialized properly
        """
        if not self.foodsens.initialized:
            try:
                self.foodsens.initialize()
            except Exception as e:
                raise RuntimeError(e)
            
    def startCamera(self):
        """
        Run the start() method for the camera object
        
        Args:         
            None
            
        Returns:
            None
            
        Raises:
            RuntimeError if the camera object is not initialized properly
        """
        if self.picam.initialized:
            try:
                self.picam.start()
            except Exception as e:
                raise RuntimeError(e)
        else:
            raise RuntimeError("Camera not initialized.")
        
    def stopCamera(self):
        """
        Run the cleanup() method for the camera object
        
        Args:         
            None
            
        Returns:
            None
            
        Raises:
            RuntimeError if the camera object is not initialized properly
        """
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
            self._initializeDisplay()
            self.hardwareInitialized["display"] = True
        if not self.hardwareInitialized["motor"] and self.hardwareEnabled["motor"]:
            self._initializeMotor()
            self.hardwareInitialized["motor"] = True
        if not self.hardwareInitialized["picam"] and self.hardwareEnabled["picam"]:
            self._initializeCamera()
            self.hardwareInitialized["picam"] = True
        if not self.hardwareInitialized["foodsens"] and self.hardwareEnabled["foodsens"]:
            self._initializeDistanceSensor()
            self.hardwareInitialized["foodsens"] = True
                    
        