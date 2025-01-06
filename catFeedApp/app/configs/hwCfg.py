class HardwareConfig:
    # Define GPIOs
    GPIOS = {
        "DSENS_TRIG" : 16,
        "DSENS_ECHO" : 20,
        "DC_MOTOR_EN1" : 19,
        "DC_MOTOR_EN2" : 26
    }
    # Define LCD parameters
    LCD = {
        "LCD_I2C_ADDR" : 0x27,
        "ROWS" : 4,
        "COLS" : 20
    }
    # Define camera parameters
    CAMERA = {
        "RESOLUTION" : (1080, 1080),     # Default resolution 720p
        "MAX_RESOLUTION" : (1920, 1080),
        "V_FLIP" : True,
        "H_FLIP" : False,
        "ROTATION" : 0
    }
    # Define hardware enablement
    HW_ENABLE = {
        "DISPLAY" : False,
        "CAMERA" : True,
        "MOTOR" : True,
        "DSENS" : False
    }
