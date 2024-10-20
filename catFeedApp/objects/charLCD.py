from smbus2 import SMBus
from time import sleep
import threading

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
        self.screen_buffer = [[' ' for x in range(20)] for y in range(4)]
        self.screen_buffer_stack = []
        self.panes = []
        self.paneIndex = 0
        self.paneCount = 0
        self.cursorPostion = [0, 0]
        self.initialized = False
        self.lcdUpdateLock = threading.Lock()
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
            
    def _displayOn(self):
        self._lcd_send_command(self.LCD_DISPLAYCONTROL | self.LCD_DISPLAYON)
        
    def _displayOff(self):
        self._lcd_send_command(self.LCD_DISPLAYCONTROL | self.LCD_DISPLAYOFF)
        
    def _clear(self):
        self._lcd_clear()
        
    def _pushScreenBuffer(self):
        currentScreenBuffer = [[' ' for i in range(self.LCD_WIDTH)] for j in range(self.LCD_HEIGHT)]
        for i in range(self.LCD_HEIGHT):
            for j in range(self.LCD_WIDTH):
                currentScreenBuffer[i][j] = self.screen_buffer[i][j]
        self.screen_buffer_stack.append(currentScreenBuffer)
        
    def _popScreenBuffer(self):
        buffer = self.screen_buffer_stack.pop()
        return buffer
    
    def _getScreenBufferTop(self):
        return self.screen_buffer_stack[-1]
    
    # When the LCD powers on, it defaults to an unknown state. The HD44780 datasheet specifies that after power-up, 
    # the LCD might be in 8-bit mode, but there's no guarantee about its mode or configuration. The initialization 
    # process is designed to reset the LCD and configure it properly.
    def initialize(self):
        try:
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
        
    def _writeScreen(self, array):
        self._clear()
        for i in range(min(self.LCD_HEIGHT, len(array))):
            self.screen_buffer[i] = array[i]
            self._writeRow(i, array[i])
    
    def ephemeralDisplay(self, array, time):
        self.lcdUpdateLock.acquire()
        self._pushScreenBuffer()
        self._clear()
        for i in range(len(array)):
            self._writeRow(i, array[i])
        sleep(time)
        self._clear()
        old = self._getScreenBufferTop()
        for i in range(len(old)):
            self._writeRow(i, old[i])
        self._popScreenBuffer()
        self.lcdUpdateLock.release()
            
    def feedTimeDisplayRoutine(self,t):
        array = [[' ' for i in range(self.LCD_WIDTH)] for j in range(self.LCD_HEIGHT)]
        array[0] = "   |`__/,|   ( (    "
        array[1] = " _.|o o  |____) )   "
        array[2]=  "-(((---(((--------  "
        array[3] = "     Feed Time!     "
        self.ephemeralDisplay(array, t)
        
    def registerPane(self, name, pane):
        for i in range(len(self.panes)):
            if self.panes[i]['name'] == name:
                print("Pane " + name + " already exists")
                return
        print("Registered pane: " + name)
        newPane = {'paneData': pane, 'name': name}
        self.panes.append(newPane)
        self.paneCount = len(self.panes)
        
    def removePane(self, name):
        paneFound = False
        for i in range(len(self.panes)):
            if self.panes[i]['name'] == name:
                paneFound = True
                self.panes.pop(i)
                self.paneCount -= 1
        if not paneFound:
            print("Pane " + name + " not found")
            
    def updatePane(self, name, data):
        paneFound = False
        # Verify that the pane exists
        for i in range(len(self.panes)):
            if self.panes[i]['name'] == name:
                # Update the pane data
                paneFound = True
                self.panes[i]['paneData'] = data
        # If the pane was found and the updated pane is the currently displayed pane, update the screen
        with self.lcdUpdateLock:
            if paneFound and self.panes[self.paneIndex]['name'] == name:
                self._writeScreen(self.panes[self.paneIndex]['paneData'])
        if not paneFound:
            print("Pane " + name + " not found, cannot update content")
            
    def iteratePanes(self):
        numPanes = len(self.panes)
        with self.lcdUpdateLock:
            if self.paneIndex + 1 >= numPanes:
                self.paneIndex = 0
            else:
                self.paneIndex += 1
            print("Iterating pane: " + self.panes[self.paneIndex]['name'])
            self._writeScreen(self.panes[self.paneIndex]['paneData'])
            
    

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
    


