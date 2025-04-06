from picamera2 import Picamera2

VALID_RESOLUTIONS = [(640, 480), (1280, 720), (1920, 1080)]

class Camera:
    """
    Class wrapping a Picamera2 object
    """
    def __init__(self, resolution=(640, 480)):
        """
        Initialize the camera object basic properties
        
        Args:
            resolution: The resolution of the camera in pixels (width, height)
            
        Returns:
            None
        """
        self.res = resolution
        self.camera = None
        self.initialized = False
    
    def initialize(self):
        """
        Initializes the Picamera2 object, configuring it with the specified resolution
        
        Args:
            None
            
        Returns:
            None
        """
        try:
            print("Initializing camera with resolution: " + str(self.res))
            if self.camera:
                self.camera.stop()
                self.camera.close()
            self.camera = Picamera2()
            self.cam_config = self.camera.create_preview_configuration(main={"size": self.res})
            self.camera.configure(self.cam_config)
            # self.camera.set_preview_transform(picamera2.PreviewTransform(hflip=True, vflip=True, rotation=picamera2.Transform.Rotation.ROTATION_90))
            self.initialized = True
            return True
        except Exception as e:
            raise RuntimeError(e)
        
    def start(self):
        """
        Starts the Picamera2 object
        
        Args:            
            None
            
        Returns:
            None
        """
        self.camera.start()
        
    def cleanup(self):
        """
        Stops and closes the Picamera2 object
        
        Args:            
            None
            
        Returns:
            None
        """
        if self.camera:
            self.camera.stop()
            self.camera.close()
            
        self.initialized = False
        
    def setResolution(self, resolution):
        """
        Sets the resolution of the camera
        
        Args:
            resolution: The resolution of the camera in pixels (width, height)
            
        Returns:
            True if the resolution is valid, False otherwise
        """
        # Verify that the resolution is valid
        if resolution in self.VALID_RESOLUTIONS:
            self.res = resolution
            self.cam_config = self.camera.create_preview_configuration(main={"size": resolution})
            self.camera.configure(self.cam_config)
            return True
        else:
            return False
