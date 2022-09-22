
from RPLCD.i2c import CharLCD


screen = CharLCD(i2c_expander = 'PCF8574',address = 0x27, cols = 20, rows = 4, backlight_enabled = True)


screen.write_string("Raspberry Pi Test")

screen.cursor_pos=(2,0)
screen.write_string("Hello world!")
screen.cursor_pos=(3,10)
screen.write_string(">.<")


class charLCD:
    screen = CharLCD(i2c_expander = 'PCF8574', address = 0x27, cols = 20, rows = 4, backlight_enabled = True)
    def write(self, string):
        if(isinstance(string,str)):
            self.screen.write_string(string)
            return
        else:
            return
    def clear(self):
        self.screen.clear()
        return
    def setCursor(self,row,col):
        if(row < 4 and col <= 20):
            self.screen.cursor_pos = (row,col)
            return
    def linefeed(self):
        self.screen.cr()
