import os
import time
import lib.signs as signs
import random
from utils import Utils
from lib.bmp_reader import BMPReader

try:
    from machine import Pin, I2C
    _DEBUG_MODE = False
except ImportError or ModuleNotFoundError:
    import termcolor
    _DEBUG_MODE = True

if (not _DEBUG_MODE):
    from lib.neopixel import Neopixel  

columns = range(8)
black = (0, 0, 0)

class LedPainter:
  def __init__(self, num_leds, state_machine, pin, mode="RGB", delay=0.0001, options = False, settings = False):
    self.options = options
    self.colors = settings['sources']['colors']
    self.num_leds = num_leds
    self.speed = options['speed']['value']
    self.brightness = options['brightness']['value']
    self.pixelate = self.options['pixelate']['value']
    self.upper_fire = 0
    if (not _DEBUG_MODE):
      self.strip = Neopixel( num_leds, state_machine, pin, mode, delay)
      self.strip.brightness(self.brightness)

  def initialAnimation(self):
    color = self.getColor('red')
    for pixel in range(self.num_leds):
      if (not _DEBUG_MODE):
        ##self.strip.fill(black)
        self.strip.set_pixel(pixel, color)
        self.strip.show()
        time.sleep(self.speed/50)
    if (not _DEBUG_MODE):        
     self.strip.fill(black)
     self.strip.show()
    
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
      text_color = Utils.hex2rgb(self.colors[self.options['text_color']['value']-1]['value'])
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
      if not _DEBUG_MODE and self.pixelate == 1:
         self.strip.fill(black)
         self.strip.show()
         time.sleep(self.speed/20)

  def image(self,filename):
    img = BMPReader(filename)
    for x in range(img.width-1,-1,-1):
        y=0
        for column_pixel in img.read_column_pixels(x):          
          if (not _DEBUG_MODE and y <= self.num_leds):self.strip.set_pixel(y,column_pixel)
          else:self.printPixel(column_pixel, str(x)+','+str(y))
          y+=1
        if (not _DEBUG_MODE):
          self.strip.show()
          time.sleep(self.speed)
        else: 
          time.sleep(self.speed)
          print('-----' + filename + '--------')
          #os.system('cls') 
        if not _DEBUG_MODE and self.pixelate == 1:
          self.strip.fill(black)
          self.strip.show()
          time.sleep(self.speed/20)

  def printSigns(self,text, oled):
    for letter in text:
      self.printSign(letter, oled)
      if (not _DEBUG_MODE):
        self.strip.fill(black)
        self.strip.show()
      time.sleep(self.speed/5)

  def gradient(self,color1, color2):
      color1 = Utils.hex2rgb(self.colors[color1]['value'])
      color2 = Utils.hex2rgb(self.colors[color2]['value'])
      if (not _DEBUG_MODE):
        self.strip.set_pixel_line_gradient(0, self.num_leds-1, color1,color2)
        self.strip.show()
      else:print('displaying gradient')

  def fire(self):
      color1 = self.getColor('red')
      color2 = self.getColor('yellow') 
      if (not _DEBUG_MODE):
        self.strip.fill(black)
        sign = random.randint(-1,1)
        inc = random.randint(0,3)
        if (self.upper_fire + sign*inc < 0 or self.upper_fire + sign*inc > self.num_leds-1):sign = -sign
        self.upper_fire += sign*inc
        self.strip.set_pixel_line_gradient(0, self.upper_fire, color2,color1)
        self.strip.show()
      else:print('displaying fire' + str(self.upper_fire))

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

  def printPixel(self, color, text = ''):
    if (color == self.getColor('red')):
        tcolor = 'red'
    elif (color == self.getColor('green')):
        tcolor = 'green'
    elif (color == self.getColor('blue')):
        tcolor = 'blue'
    elif (color == self.getColor('black')):
        tcolor = 'black'
    elif (color == self.getColor('white')):
        tcolor = 'white'
    else: tcolor = 'white'
    termcolor.cprint("\u25A0 " + text + '(' + str(color) + ')',tcolor)