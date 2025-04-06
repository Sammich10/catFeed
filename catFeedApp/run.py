from app import create_app, get_camera
import os
from app.configuration import HardwareConfig as hwConfig
      
if __name__ == "__main__":
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        # initialize the feeder and start the camera
        pass
    app = create_app()
    app.run(host="0.0.0.0", port = "5000", debug=True)