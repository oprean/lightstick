import os
import time
import signs as signs
import json

try:
    from machine import Pin, I2C
    _DEBUG_MODE = False
except ImportError or ModuleNotFoundError:
    _DEBUG_MODE = True

if (not _DEBUG_MODE):
    from neopixel import Neopixel  

columns = range(8)

red = (255, 255, 0)
black = (0, 0, 0)
#pixels.brightness(10)

class obj:
     
    # constructor
    def __init__(self, dict1):
        self.__dict__.update(dict1)
  
def dict2obj(dict1):
  return json.loads(json.dumps(dict1), object_hook=obj)

class LedPainter:
  def __init__(self, num_leds, state_machine, pin, mode="RGB", delay=0.0001, options = False):
    self.options =dict2obj(options)
    self.speed = options['speed']
    self.brig = options['speed']
    if (not _DEBUG_MODE):
      self.strip = Neopixel( num_leds, state_machine, pin, mode, delay)
      self.strip.brightness(self.options.brightness)
  def getSignMatrix(self, letter):
    #‘A’, it is 65 while for ‘a’, it is 97. 
    ascii = ord(letter)
    if (ascii>=97):
     t = ascii-97
    else:
      t = ascii-65
    return signs.letters[t]

  def printSign(self, letter, lcd):
    matrix = self.getSignMatrix(letter)
    if (_DEBUG_MODE):
      os.system('cls') 
      print(letter)
    else: 
      self.strip.fill(black)
      lcd.fill(0)
      lcd.text(letter, 60, 28)
      lcd.show()
    time.sleep(self.options.speed)

    for col in columns:
      if (not _DEBUG_MODE):self.strip.fill(black)
      else:os.system('cls') 

      rowcnt = 0
      for row in matrix:
        if (row[col] != '0'):
          if (_DEBUG_MODE):print("\u25A0")
          else:self.strip.set_pixel(rowcnt, red)
        else:
          if (_DEBUG_MODE):print("\u25A1")
          else:self.strip.set_pixel(rowcnt, black)
        rowcnt +=1
      if not _DEBUG_MODE:
        self.strip.show()
      time.sleep(self.options.speed)

  def printSigns(self,text, lcd):
    for letter in text:
      self.printSign(letter, lcd)
      if (not _DEBUG_MODE):
        self.strip.fill(black)
        self.strip.show()
      time.sleep(self.options.speed)