
from RPLCD.i2c import CharLCD
import os
import threading
import time


class charLCD():

    def __init__(self,_i2c_exp = 'PCF8574', _addr = 0x27, _cols = 20, _rows = 4, _backlight_en = True):
        self.cols=_cols
        self.rows=_rows
        self.charsBuffer = []
        self.linesFull= 0
        self.screenUpdater = None
        self.screenUpdaterRunning = False
        self.screen = CharLCD(i2c_expander = _i2c_exp, address = _addr, cols = _cols, rows = _rows, backlight_enabled = _backlight_en)
        self.rowOverload= False

    def getlinesfull(self):
        return self.linesFull
    
    def isScreenUpdaterRunning(self):
        return self.screenUpdaterRunning

    def getCols(self):
        return self.cols

    def getRows(self):
        return self.rows

    def clear(self):
        while self.charsBuffer:
            self.charsBuffer.pop()
        self.screen.clear()
        self.linesFull = 0
        return
  
    def setCursor(self,row,col):
        if(row < self.rows and col <= self.cols):
            self.screen.cursor_pos = (row,col)
            return

    #takes a matrix the size of the screen and writes it to the screen
    #not meant to be used directly
    def _write_to_screen(self,matrix):
        if len(matrix) > self.rows:
            return False
        str_concat = ""
        for row in matrix:
            if len(row) != self.cols:
                return False
            for element in row:
                if not isinstance(element,str):
                    return False
                else:
                    str_concat += element
        
        self.screen.cursor_pos = (0,0)
        self.screen.write_string(str_concat)
        return True


    #write a string into the row number specified (1-self.row) not zero indexed
    def writeRow(self,_row,string):
        #basic error checking
        if(not isinstance(string,str)):
            print("Error: row insert not a string")
            return
        
        if(len(string)>self.cols):
            print("Error: row insert string characters exceeds columns")
            return
        
        if(_row<1):
            print("Error: row insert row less than 1")
            return
        
                
        if(_row>self.linesFull):
            for n in range(self.linesFull, _row):
                blank_row = [" " for i in range(self.cols)]
                self.charsBuffer.insert(n,blank_row)
                self.linesFull+=1
            if(self.linesFull > self.rows):
                self.rowOverload=True
            self.linesFull = _row
        else:
            #if selected row already exists (_row < self.linesFull) clear the content of that row
            self.charsBuffer[_row-1] = [" " for i in range(self.cols)]
        for n,ch in enumerate(string):
            self.charsBuffer[_row-1][n] = ch
        #if(not self._write_to_screen(self.charsBuffer)):
        #    print("Error writing to screen")
        return

    def pop_row(self,_row_number):
        if(_row_number < 1 or _row_number > self.linesFull):
            print("Error deleting row: row number invalid!")
            return
        self.charsBuffer.pop(_row_number)

    def startUpdaterThread(self):
        if not self.screenUpdaterRunning:
            self.screenUpdater = threading.Thread(target=self.update, group=None)
            self.screenUpdaterRunning = True
            self.screenUpdater.start()

    def stopScreenUpdater(self):
        if self.screenUpdaterRunning:
            self.screenUpdaterRunning = False
            self.screenUpdater.join()
            self.screenUpdater = None

    def update(self):
        while(True):
            if(self.linesFull < self.rows):
                self._write_to_screen(self.charsBuffer)
            elif(self.rowOverload):
                self._write_to_screen(self.charsBuffer)
            time.sleep(.5)    

        return
