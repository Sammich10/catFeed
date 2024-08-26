from smbus2 import SMBus
from time import sleep

class CharLCD:
    # This class is used to control the character LCD using the Raspberry Pi's I2C interface
    # It is based on the PCF8574A I2C I/O expander
    def __init__(self, address=0x27, bus=1, width = 20, height = 4):
        # Initialize the LCD

        # Parameters
        # ----------
        # address : int, optional
        #     The I2C address of the PCF8574, often 0x27 or 0x3F.
        # bus : int, optional
        #     The I2C bus number, often 1 or 0.
        self.address = address
        self.bus = SMBus(bus)
        # Internal buffer representation of the screen as a 4x20 array of characters.
        # This list will be able to contain additional rows so the screen can be scrolled.
        self.screen = [[' ' for x in range(20)] for y in range(4)]
        self.cursorPostion = [0, 0]
    # Write a single byte to the PCF8574 via I2C
    def _write_byte(self, data):
        self.bus.write_byte(self.address, data | self.LCD_BACKLIGHT)

    # Toggle the enable pin on the LCD to process a command
    def _toggle_enable(self, data):
        # Pulse the enable pin
        sleep(self.E_DELAY)
        self._write_byte(data | 0b00000100)  # E high
        sleep(self.E_PULSE)
        self._write_byte(data & ~0b00000100)  # E low

    # Write 4 bits of data to the LCD
    def _write_four_bits(self, data):
        self._write_byte(data)
        self._toggle_enable(data)

    # Send a command to the LCD
    def _lcd_send_command(self, command):
        self._write_four_bits(command & 0xF0)
        self._write_four_bits((command << 4) & 0xF0)

    # Send a character to the LCD
    def _lcd_send_char(self, char):
        self._write_four_bits(self.LCD_BACKLIGHT | 0b00000001 | (char & 0xF0))
        self._write_four_bits(self.LCD_BACKLIGHT | 0b00000001 | ((char << 4) & 0xF0))
    
    # When the LCD powers on, it defaults to an unknown state. The HD44780 datasheet specifies that after power-up, 
    # the LCD might be in 8-bit mode, but there's no guarantee about its mode or configuration. The initialization 
    # process is designed to reset the LCD and configure it properly.
    def _lcd_init(self):
        # Send 0x03 to wake up the LCD and  ensure it is in 8-bit mode
        self._lcd_send_command(0x03)
        self._lcd_send_command(0x03)
        self._lcd_send_command(0x03)
        # Send 0x02 to switch to 4-bit mode
        self._lcd_send_command(0x02)

        # Setup the display
        self._lcd_send_command(self.LCD_FUNCTIONSET | self.LCD_4BITMODE | self.LCD_2LINE | self.LCD_5x8DOTS)
        self._lcd_send_command(self.LCD_DISPLAYCONTROL | self.LCD_DISPLAYON)
        self._lcd_send_command(self.LCD_CLEARDISPLAY)
        self._lcd_send_command(self.LCD_ENTRYMODESET | self.LCD_ENTRYLEFT)
        sleep(0.2)

    # Clear the display
    def _lcd_clear(self):
        self._lcd_send_command(self.LCD_CLEARDISPLAY)
        sleep(0.002)

    # Write a string of characters to the LCD
    def _lcd_write_string(self, string):
        for char in string:
            self._lcd_send_char(ord(char))

    # Set the cursor position
    def _lcd_set_cursor(self, col, row):
        row_offsets = [0x00, 0x40, 0x14, 0x54]
        self._lcd_send_command(self.LCD_SETDDRAMADDR | (col + row_offsets[row]))
        self.cursorPostion = [col, row]
        
    def writeRow(self, row, string):
        self._lcd_set_cursor(0, row)
        maxLength = self.LCD_WIDTH
        # If the string is too long, truncate it
        if len(string) > maxLength:
            string = string[:maxLength]
        self._lcd_write_string(string)
        self._lcd_set_cursor(0, row + 1)
        
    def writeStringToPos(self, col, row, string):
        self._lcd_set_cursor(col, row)
        # If the string is too long, truncate it
        if len(string) > self.LCD_WIDTH - col:
            string = string[:self.LCD_WIDTH - col]
        self._lcd_write_string(string)
        
    def writeCharToPos(self, col, row, char):
        if(col > self.LCD_WIDTH - 1) and (row > self.LCD_HEIGHT - 1):
            self._lcd_set_cursor(col, row)
            self._lcd_send_char(ord(char))
            
    def displayOn(self):
        self._lcd_send_command(self.LCD_DISPLAYCONTROL | self.LCD_DISPLAYON)
        
    def displayOff(self):
        self._lcd_send_command(self.LCD_DISPLAYCONTROL | self.LCD_DISPLAYOFF)
        
    def clear(self):
        self._lcd_clear()
        
    def initialize(self):
        self._lcd_init()
            
        

    LCD_BACKLIGHT = 0x08
    LCD_NOBACKLIGHT = 0x00

    # Timing constants
    E_PULSE = 0.0005                    # Duration of the enable pulse in seconds
    E_DELAY = 0.0005                    # Delay between enable pulses in seconds

    # LCD Commands
    LCD_CLEARDISPLAY = 0x01             # Clear display
    LCD_RETURNHOME = 0x02               # Return cursor to home position (0,0)
    LCD_ENTRYMODESET = 0x04             # Set entry mode
    LCD_DISPLAYCONTROL = 0x08           # Control display on/off and cursor blink
    LCD_CURSORSHIFT = 0x10              # Shift cursor
    LCD_FUNCTIONSET = 0x20              # Set function of display
    LCD_SETCGRAMADDR = 0x40             # Set character generator RAM address
    LCD_SETDDRAMADDR = 0x80             # Set data DRAM address

    # Flags for display entry mode
    LCD_ENTRYRIGHT = 0x00
    LCD_ENTRYLEFT = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00

    # Flags for display on/off control
    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00

    # Flags for function set
    LCD_8BITMODE = 0x10
    LCD_4BITMODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00
    LCD_5x10DOTS = 0x04
    LCD_5x8DOTS = 0x00
    
    # Class operational modes
    PANE_VIEW_MODE = 0
    SLIDE_VIEW_MODE = 1
    
    # Class variables and constants
    LCD_WIDTH = 20
    LCD_HIEGH = 4
    


