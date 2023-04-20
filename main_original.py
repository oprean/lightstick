_DEBUG_MODE = False
if (not _DEBUG_MODE):
    import ssd1306
    from machine import Pin, I2C
    from navkeys import NavKeyboard
    #up_pin, right_pin, down_pin, left_pin, select_pin
    keyboard = NavKeyboard(1,20,19,4,18)
else:
    import keyboard    
from ledpainter import LedPainter
import time
import os
import json

###### constants ##########  
_START_PAGE = 'home'
if (not _DEBUG_MODE):
    _JSON_MENU = 'menu.json'
    _JSON_SETTINGS = 'settings.json'
else:
    _JSON_MENU = 'C:\Personal\pico\code\Lightstick\menu.json'
    _JSON_SETTINGS = 'C:\Personal\pico\code\Lightstick\settings.json'

_UP = 0
_RIGHT = 1
_DOWN = 2
_LEFT = 3

_NUM_PIXEL = 30

# "neighbours":["top","right","bottom","left"]

if (not _DEBUG_MODE):
    i2c = I2C(0, sda=Pin(16), scl=Pin(17))
    lcd = ssd1306.SSD1306_I2C(128, 64, i2c)
else:
    lcd = print
strip = LedPainter(_NUM_PIXEL, 0, 28, "GRB")

class Lightstick:
    def __init__(self, json_menu_file, json_settings_file, selected=_START_PAGE):
        self.selected = selected
        self.in_action = False
        f = open(json_menu_file)
        self.menu = json.load(f)
        self.menu = self.menu['menu']
        f.close()

        f = open(json_settings_file)
        self.settings = json.load(f)
        f.close()

        for page in self.menu:
            #print(page)
            if (page['name'] == self.selected):
                self.page = page

    def drawPageHeader(self):
        udarrows = ''
        lrarrows = ''
        if (self.page['neighbours'][_UP]!=''): 
            if (_DEBUG_MODE):udarrows +='\u25B2'
            else:lcd.hline(1,1,128,1)
        if (self.page['neighbours'][_DOWN]!=''): 
            if (_DEBUG_MODE):udarrows +='\u25BC'
            else:lcd.hline(1,11,128,1)
        if (self.page['neighbours'][_LEFT]!=''): 
            if (_DEBUG_MODE):lrarrows +='\u25C4'
            else:lcd.vline(1,1,11,1)            
        if (self.page['neighbours'][_RIGHT]!=''): 
            if (_DEBUG_MODE):lrarrows +='\u25BA'
            else:lcd.vline(127,1,11,1)


        if (_DEBUG_MODE):print(lrarrows+' '+self.page['label']+' '+udarrows)
        else:lcd.text(self.page['label'], 2, 3)

    def drawPageContent(self):
        if (self.page['type'] == 'static'):            
            if (_DEBUG_MODE):print(self.page['content'])
            else:lcd.text(self.page['content'], 2, 14)
        elif (self.page['type'] == 'settings' and self.selected in self.settings):
            if (self.in_action):
                if (_DEBUG_MODE):print(self.settings[self.selected])
                else:lcd.rect(10, 12, self.settings[self.selected],24,1)
            else:
                if (_DEBUG_MODE):print(self.settings[self.selected])
                else:lcd.text(self.page['content'] + ' ' +str(self.settings[self.selected]), 2, 12)
        elif (self.page['type'] == 'presets'):
            if (_DEBUG_MODE):print(self.page['content'])
            else:lcd.text(self.page['content'], 2, 12)

    def draw(self):
            if (_DEBUG_MODE):os.system('cls')
            else:lcd.fill(0)
            self.drawPageHeader()
            self.drawPageContent()
            if (not _DEBUG_MODE):lcd.show()      

    def readKey(self):
        i = -1
        key = keyboard.read_key()
        time.sleep(.2)
        if key == 'up':
            self.selected = self.page['neighbours'][_UP]
        elif key == 'right':
            self.selected = self.page['neighbours'][_RIGHT]
        elif key == 'down':            
            self.selected = self.page['neighbours'][_DOWN]
        elif key == 'left':
            self.selected = self.page['neighbours'][_LEFT]
        elif key == 'enter' and not self.in_action:
            if 'action' in self.page:
                action = getattr(self, self.page['action'])
                action()
        for page in self.menu:
            if (page['name'] == self.selected):
                self.page = page
        self.draw()

## ACTIONS ##############
    def update_setting(self):
        if  self.selected in self.settings:
            self.in_action = True
            inc = 1
            self.draw()
            while self.in_action == True:
                key = keyboard.read_key()
                time.sleep(.2)
                if (key == 'enter'):
                    self.in_action = False
                    break
                elif (key == 'right'):
                    self.settings[self.selected] += inc
                elif (key == 'left'):
                    self.settings[self.selected] += -inc

                with open(_JSON_SETTINGS, 'w') as f:
                    json.dump(self.settings, f)
                self.draw()

## PRESETS ###############
    def preset_rainbow(self):
        print("running rainbow")
        self.in_action = True
        self.draw()
        while True:
            key = keyboard.read_key()
            time.sleep(.2)
            if (key == 'enter'):
                self.in_action = False
                break
            strip.rainbow()
            self.draw()

    def preset_text(self):
        self.in_action = True
        self.draw()
        strip.printSigns('M', lcd)
        self.in_action = False
        self.draw()

######## start the program here #####

stick = Lightstick(_JSON_MENU, _JSON_SETTINGS, _START_PAGE)
stick.draw()
print(os.uname().sysname)
while True:
    stick.readKey()

