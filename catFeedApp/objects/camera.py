import picamera2
import atexit
from picamera2 import Picamera2

class Camera:
    def __init__(self, resolution=(640, 480)):
        self.res = resolution
        self.camera = None
        self.initialized = False
    
    def initialize(self):
        print("Initializing camera with resolution: " + str(self.res))
        try:
            if self.camera:
                self.camera.stop()
                self.camera.close()
            self.camera = Picamera2()
            self.cam_config = self.camera.create_preview_configuration(main={"size": self.res})
            self.camera.configure(self.cam_config)
            # self.camera.set_preview_transform(picamera2.PreviewTransform(hflip=True, vflip=True, rotation=picamera2.Transform.Rotation.ROTATION_90))
            self.initialized = True
        except Exception as e:
            raise RuntimeError(e)
        
    def start(self):
        self.camera.start()
        
    def cleanup(self):
        if self.camera:
            self.camera.stop()
            self.camera.close()
            
        self.initialized = False
        
    def setResolution(self, resolution):
        # Verify that the resolution is valid
        if resolution in self.VALID_RESOLUTIONS:
            self.res = resolution
            self.cam_config = self.camera.create_preview_configuration(main={"size": resolution})
            self.camera.configure(self.cam_config)
            return True
        else:
            return False
            
    VALID_RESOLUTIONS = [(640, 480), (1280, 720), (1920, 1080)]