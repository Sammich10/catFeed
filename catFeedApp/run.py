from app import create_app, initialize_hardware, shutdown_hardware
import os, atexit
from app.configuration import HardwareConfig as hwConfig
      
if __name__ == "__main__":
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        # initialize the feeder and start the camera
        pass
    app = create_app()
    # If this is the first time the app is being run, initialize the hardware
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        initialize_hardware()    
    # Register the shutdown function
    atexit.register(shutdown_hardware)
    
    app.run(host="0.0.0.0", port = "5000", debug=True)