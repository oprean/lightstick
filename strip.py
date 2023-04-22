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
black = (0, 0, 0)

def hex2rgb(hex):
  return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

class LedPainter:
  def __init__(self, num_leds, state_machine, pin, mode="RGB", delay=0.0001, options = False, settings = False):
    self.options = options
    self.settings = settings
    self.num_leds = num_leds
    self.speed = options['speed']
    self.brightness = options['brightness']
    if (not _DEBUG_MODE):
      self.strip = Neopixel( num_leds, state_machine, pin, mode, delay)
      self.strip.brightness(self.brightness)

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
      text_color = hex2rgb(self.settings['colors'][self.options['text_color']])
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
      color1 = hex2rgb(self.settings['colors'][color1])
      color2 = hex2rgb(self.settings['colors'][color2])
      if (not _DEBUG_MODE):
        self.strip.set_pixel_line_gradient(0, self.num_leds-1, color1,color2)
        self.strip.show()
      else:print('displaying gradient')

  #https://www.krishnamani.in/color-codes-for-rainbow-vibgyor-colours/
  def rainbow(self):
    colors = self.settings['colors']
    rainbow = [colors['violet'], colors['indigo'], colors['blue'], colors['green'], colors['yellow'], colors['orange'], colors['red']]
    i = 0
    if (not _DEBUG_MODE):
      self.strip.fill(black)
      for color in rainbow:
        color = hex2rgb(color)
        self.strip.set_pixel(i*4, color)
        self.strip.set_pixel(i*4+1, color)
        self.strip.set_pixel(i*4+2, color)
        self.strip.set_pixel(i*4+3, color)
        i +=1
      self.strip.show()
    else:print('displaying rainbow')