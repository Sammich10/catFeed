from smbus2 import SMBus
from time import sleep
import threading

class CharLCD:
    """
    This class is used to control the character LCD using the Raspberry Pi's I2C interface
    It is based on the PCF8574A I2C I/O expander
    """
    def __init__(self, address = 0x27, bus = 1, width = 20, height = 4):
        """
        Initialize the LCD

        Params:
            address
                The I2C address of the PCF8574, often 0x27 or 0x3F.
            bus
                The I2C bus number, often 1 or 0.
        Returns:
            None
        """
        
        # Initialize class variables from constructor parameters
        self.address = address
        self.LCD_WIDTH = width
        self.LCD_HEIGHT = height
        
        # Initialize the SMBus interface
        self.bus = SMBus(bus)
        
        self.initialized = False
        
    def _write_byte(self, data):
        """
        Write a single byte to the PCF8574 via I2C interface

        Params:
            data
                The byte to write to the PCF8574
        Returns:
            None
        """
        
        self.bus.write_byte(self.address, data | self.LCD_BACKLIGHT)

    def _toggle_enable(self, data):
        """
        Pulses the enable pin on the LCD to process a command

        Params:
            data
                The byte to write to the PCF8574
        Returns:
            None
        """
        
        # Pulse the enable pin HIGH
        sleep(self.E_DELAY)
        self._write_byte(data | 0b00000100)  # E high
        
        # Pulse the enable pin LOW
        sleep(self.E_PULSE)
        self._write_byte(data & ~0b00000100)  # E low

    def _write_four_bits(self, data):
        """
        Writes the data to the PCF8574 via I2C interface and toggles the enable pin to process the command
        
        Params:
            data
                The byte to write to the PCF8574
        Returns:
            None
        """
        
        # Write the data to the PCF8574
        self._write_byte(data)
        
        # Pulse the enable pin
        self._toggle_enable(data)

    def _lcd_send_command(self, command):
        """
        Sends a command to the LCD by writing the upper and lower nibbles of the command to the LCD
        
        Params:
            command
                The command to send to the LCD (expected to be a byte)
        Returns:
            None
        """
        
        # Send the upper nibble
        self._write_four_bits(command & 0xF0)

        # Send the lower nibble
        self._write_four_bits((command << 4) & 0xF0)

    def _lcd_send_char(self, char):
        """
        Sends a character to the LCD to be written to the current cursor position
        
        Params:
            char
                The character to send to the LCD (expected to be a byte)
        Returns:
            None
        """
        
        # Send the upper nibble of the character
        self._write_four_bits(self.LCD_BACKLIGHT | 0b00000001 | (char & 0xF0))
        
        # Send the lower nibble of the character
        self._write_four_bits(self.LCD_BACKLIGHT | 0b00000001 | ((char << 4) & 0xF0))

    def _lcd_clear(self):
        """
        Clears the LCD by sending the clear display command
        
        Params:
            None
        Returns:
            None
        """
        
        # Send the clear display command
        self._lcd_send_command(self.LCD_CLEARDISPLAY)
        
        # Wait for the clear command to complete before returning
        sleep(0.002)

    def _lcd_write_string(self, string):
        """
        Write a string of characters to the LCD starting at the current cursor position
        
        Params:
            string
                The string of characters to write to the LCD
        Returns:
            None
        """
        
        # Iterate through each character in the string and send it to the LCD
        for char in string:
            self._lcd_send_char(ord(char))

    # Set the cursor position
    def _lcd_set_cursor(self, col, row):
        """
        Set the cursor position on the LCD
        
        Params:
            col
                The column to set the cursor to (0-15)
            row
                The row to set the cursor to (0-3)
        Returns:
            None
        """
        
        # Set the cursor position
        self._lcd_send_command(self.LCD_SETDDRAMADDR | (col + self.ROW_OFFSETS[row]))
        
        # Update the cursor position
        self.cursorPostion = [col, row]
        
    def _displayOn(self):
        """
        Turn on the LCD display
        
        Params:
            None
        Returns:
            None
        """
        self._lcd_send_command(self.LCD_DISPLAYCONTROL | self.LCD_DISPLAYON)
        
    def _displayOff(self):
        """
        Turn off the LCD display
        
        Params:
            None
        Returns:
            None
        """
        self._lcd_send_command(self.LCD_DISPLAYCONTROL | self.LCD_DISPLAYOFF)
        
    def _writeRow(self, row, string):
        # If the string is too long, truncate it
        if len(string) > self.LCD_WIDTH:
            string = string[:self.LCD_WIDTH]
        if len(string) == 0:
            return
        self._lcd_set_cursor(0, row)
        # Place the string in the buffer
        self.screen_buffer[row] = string
        self._lcd_write_string(string)
        
    def _writeStringToPos(self, col, row, string):
        self._lcd_set_cursor(col, row)
        # If the string is too long, truncate it
        if len(string) > self.LCD_WIDTH - col:
            string = string[:self.LCD_WIDTH - col]
        # Place the string in the buffer
        self.screen_buffer[row][col] = string
        self._lcd_write_string(string)
        
    def _writeCharToPos(self, col, row, char):
        if(col > self.LCD_WIDTH - 1) and (row > self.LCD_HEIGHT - 1):
            self._lcd_set_cursor(col, row)
            self._lcd_send_char(ord(char))
        
    def _clear(self):
        self._lcd_clear()
    
    def _writeScreen(self, array):
        self._clear()
        for i in range(min(self.LCD_HEIGHT, len(array))):
            self.screen_buffer[i] = array[i]
            self._writeRow(i, array[i])
    
    def initialize(self):
        """
        Initializes the character LCD display by sending initialization commands
        
        Args:
            None
            
        Returns:
            None
        """
        try:
            # When the LCD powers on, it defaults to an unknown state. The HD44780 datasheet specifies that after power-up, 
            # the LCD might be in 8-bit mode, but there's no guarantee about its mode or configuration. The initialization 
            # process is designed to reset the LCD and configure it properly.
            
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
        except Exception as e:
            raise RuntimeError(e)
        self.initialized = True
            
    # LCD constants
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
    LCD_HEIGHT = 4
    
    ROW_OFFSETS = [0x00, 0x40, 0x14, 0x54]
    
    feedTimeAsciiArt = [
        ["   |`__/,|   ( (    "],
        [" _.|o o  |____) )   "],
        ["-(((---(((--------  "],
        ["     Feed Time!     "]
    ]
    