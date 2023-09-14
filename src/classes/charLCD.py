
from RPLCD.i2c import CharLCD
import threading, time

from RPLCD.i2c import CharLCD

class LCDController:
    def __init__(self, i2c_port, i2c_address, cols=24, rows=4):
        self.lcd = CharLCD(i2c_expander='PCF8574', address=i2c_address,
                           port=i2c_port, cols=cols, rows=rows)
        self.cols = cols
        self.rows = rows

    def clear(self):
        self.lcd.clear()

    def home(self):
        self.lcd.home()

    def set_cursor(self, col, row):
        self.lcd.cursor_pos = (col, row)

    def write_text(self, text):
        self.lcd.write_string(text)

    def scroll_left(self):
        self.lcd.shift_display_left()

    def scroll_right(self):
        self.lcd.shift_display_right()

    def create_custom_char(self, char_num, char_data):
        self.lcd.create_char(char_num, char_data)

    def display_custom_char(self, char_num):
        self.lcd.write_custom_char(char_num)

    def display_on(self):
        self.lcd.display_enabled = True

    def display_off(self):
        self.lcd.display_enabled = False

    def cursor_on(self):
        self.lcd.cursor_mode = CharLCD.CURSOR_UNDERLINE

    def cursor_off(self):
        self.lcd.cursor_mode = CharLCD.CURSOR_HIDE

    def blink_on(self):
        self.lcd.blink_enabled = True

    def blink_off(self):
        self.lcd.blink_enabled = False

    def close(self):
        self.lcd.close()

