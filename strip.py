import os
import time
import signs as signs
from utils import Utils
import random
try:
    from machine import Pin, I2C
    _DEBUG_MODE = False
except ImportError or ModuleNotFoundError:
    _DEBUG_MODE = True

if (not _DEBUG_MODE):
    from neopixel import Neopixel  

columns = range(8)
black = (0, 0, 0)

class LedPainter:
  def __init__(self, num_leds, state_machine, pin, mode="RGB", delay=0.0001, options = False, settings = False):
    self.options = options
    self.colors = settings['sources']['colors']
    self.num_leds = num_leds
    self.speed = options['speed']
    self.brightness = options['brightness']
    self.upper_fire = 0
    if (not _DEBUG_MODE):
      self.strip = Neopixel( num_leds, state_machine, pin, mode, delay)
      self.strip.brightness(self.brightness)

  def getColor(self,name):
      for color in self.colors:
          if (color['name'] == name):return Utils.hex2rgb(color['value'])

  def clear(self):
    if (not _DEBUG_MODE):
        self.strip.fill(black)
        self.strip.show()

  def getSignMatrix(self, letter):
    #‘A’, it is 65 while for ‘a’, it is 97. 
    ascii = ord(letter)
    if (ascii>=97):
     t = ascii-97
    else:
      t = ascii-65
    return signs.letters[t]

  def printSign(self, letter, oled):
    matrix = self.getSignMatrix(letter)
    if (_DEBUG_MODE):
      os.system('cls') 
      print(letter)
    else: 
      self.strip.fill(black)
      oled.lcd.fill(0)
      oled.lcd.text(letter, 60, 28)
      oled.lcd.show()
    time.sleep(self.speed)

    for col in columns:
      if (not _DEBUG_MODE):self.strip.fill(black)
      else:os.system('cls') 
      text_color = Utils.hex2rgb(self.colors[self.options['text_color']['value']]['value'])
      rowcnt = 0
      for row in matrix:
        if (row[col] != '0'):
          color = text_color
          sign = "\u25A0"
        else:
          color = black
          sign = "\u25A1"
        
        if (_DEBUG_MODE):print(sign)
        else:
            self.strip.set_pixel(rowcnt*3, color)
            self.strip.set_pixel(rowcnt*3+1, color)
            self.strip.set_pixel(rowcnt*3+2, color)

        rowcnt +=1
      if not _DEBUG_MODE:
        self.strip.show()
      time.sleep(self.speed)

  def printSigns(self,text, oled):
    for letter in text:
      self.printSign(letter, oled)
      if (not _DEBUG_MODE):
        self.strip.fill(black)
        self.strip.show()
      time.sleep(self.speed)

  def gradient(self,color1, color2):
      color1 = Utils.hex2rgb(self.colors[color1]['value'])
      color2 = Utils.hex2rgb(self.colors[color2]['value'])
      if (not _DEBUG_MODE):
        self.strip.set_pixel_line_gradient(0, self.num_leds-1, color1,color2)
        self.strip.show()
      else:print('displaying gradient')

  def fire(self):
      self.strip.fill(black)
      color1 = self.getColor('red')
      color2 = self.getColor('yellow') 
      if (not _DEBUG_MODE):
        sign = random.randint(-1,1)
        inc = random.randint(0,3)
        if (self.upper_fire + sign*inc < 0 or self.upper_fire + sign*inc > self.num_leds-1):sign = -sign
        self.upper_fire += sign*inc
        self.strip.set_pixel_line_gradient(0, self.upper_fire, color2,color1)
        self.strip.show()
      else:print('displaying fire')

  #https://www.krishnamani.in/color-codes-for-rainbow-vibgyor-colours/
  def rainbow(self):
    rainbow = [8,7,6,5,4,3,2]
    i = 0
    if (not _DEBUG_MODE):
      self.strip.fill(black)
      for color in rainbow:
        color = Utils.hex2rgb(self.colors[color]['value'])
        self.strip.set_pixel(i*4, color)
        self.strip.set_pixel(i*4+1, color)
        self.strip.set_pixel(i*4+2, color)
        self.strip.set_pixel(i*4+3, color)
        i +=1
      self.strip.show()
    else:print('displaying rainbow')