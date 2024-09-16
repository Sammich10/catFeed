# Define feeder control objects with the proper GPIOs, addresses, and other config parameters
from classes.charLCD import CharLCD
from classes.DCMotor import DCMotor
from classes.distanceSensor import DistanceSensor
from classes.camera import Camera
from appMain.configs.hwCfg import hardwareAccess
import os

# Initialize the global variable `initialized` to False.
initialized = False
# Initialize the hardware config object 
lcd = hardwareAccess.display
motor = hardwareAccess.motor
camera = hardwareAccess.picam
dsens = hardwareAccess.foodsens
# Initialize the LCD screen, camera, distance sensor, and motor, and starts the 
# camera. If any of these initializations fail, it prints an error message. At the end
# of the function, it sets the global variable `initialized` to True.
def initializeClasses():
    global initialized
    # This variable is set by the Werkzeug development server when the main 
    # application is run, as opposed to when a reloader or other subprocess 
    # is run. In other words, this code checks if the application is being 
    # run directly by the development server, rather than being reloaded or 
    # run in a subprocess, thus preventing duplicate initialization.
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        print("Initializing feeder control classes")
        # Initialize the LCD screen
        try:
            hardwareAccess.display.initialize()
            hardwareAccess.picam.initialize()
            hardwareAccess.picam.start()
            hardwareAccess.foodsens.setup()
            hardwareAccess.motor.setup()
        except Exception as e:
            print(e)
            raise Exception("Error initializing feeder control objects. Verify hardware configuration.")
        initialized = True
        print("Feeder control initialized successfully")

# Closes the camera.
def cleanupClasses():
    global initialized
    if not initialized:
        print("Feeder control classes not initialized, skipping cleanup")
        return
    print("Cleaning up feeder control classes")
    if hardwareAccess.display is not None:
        # Nothing to do yet
        pass
    if hardwareAccess.motor is not None:
        # Nothing to do yet
        pass
    if hardwareAccess.picam is not None:
        # Clean up the camera object by closing the camera and stopping the preview
        hardwareAccess.picam.cleanup()
    if hardwareAccess.foodsens is not None:
        # Nothing to do yet
        pass
    initialized = False