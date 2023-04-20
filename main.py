import os
import time
import json

try:
    from machine import Pin, I2C
    _DEBUG_MODE = False
except ImportError or ModuleNotFoundError:
    _DEBUG_MODE = True

from oled import OLED
from navkeys import NavKeyboard
from strip import LedPainter

###### constants ##########  
_START_PAGE = 'home'
if (not _DEBUG_MODE):
    _JSON_OPTIONS = 'options.json'
    _JSON_SETTINGS = 'settings.json'
else:
    _JSON_OPTIONS = 'C:\Personal\pico\code\Lightstick\options.json'
    _JSON_SETTINGS = 'C:\Personal\pico\code\Lightstick\settings.json'

_UP = 0
_RIGHT = 1
_DOWN = 2
_LEFT = 3

# "neighbours":["top","right","bottom","left"]

#https://www.geeksforgeeks.org/convert-nested-python-dictionary-to-object/ ????
class obj:
    def __init__(self, dict1):
        self.__dict__.update(dict1)
  
def dict2obj(dict):
  return json.loads(json.dumps(dict), object_hook=obj)

class Lightstick:
    def __init__(self, json_settings_file, json_options_file, selected=_START_PAGE):
        self.selected = selected
        self.in_action = False
        f = open(json_settings_file)
        self.setings = json.load(f)
        #self.setings = dict2obj(self.setings)
        self.menu = self.setings['menu']
        f.close()

        f = open(json_options_file)
        self.options = json.load(f)
        f.close()

        for page in self.menu:
            if (page['name'] == self.selected):
                self.page = page

        # init harware
        # LED STRIP
        setings = self.setings['strip']
        self.strip = LedPainter(setings['num_pixels'], setings['state_machine'], setings['pin'], setings['mode'], setings['delay'], self.options)
        
        # OLED Display
        setings = self.setings['oled']
        self.display = OLED(setings['id'], setings['sda_pin'], setings['scl_pin'])

        # NAV Keys
        setings = self.setings['navkeys']
        self.wait_key = setings['wait']
        self.keyboard = NavKeyboard(setings["up_pin"], setings["right_pin"], setings["down_pin"], setings["left_pin"], setings["select_pin"])

    def readKey(self):
        key = self.keyboard.read_key()
        time.sleep(self.wait_key)
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
        self.drawPage()

    def drawPage(self):
        self.display.draw(self.page, self.in_action, self.options)

    def update_setting(self):
        if  self.selected in self.options:
            self.in_action = True
            inc = 1
            self.drawPage()
            while self.in_action == True:
                key = self.keyboard.read_key()
                time.sleep(self.wait_key)
                if (key == 'enter'):
                    self.in_action = False
                    break
                elif (key == 'right'):
                    self.options[self.selected] += inc
                elif (key == 'left'):
                    self.options[self.selected] += -inc

                with open(_JSON_SETTINGS, 'w') as f:
                    json.dump(self.options, f)
                self.drawPage()

############# PRESETS ###############
    def preset_rainbow(self):
        self.in_action = True
        self.drawPage()
        self.strip.rainbow()
        self.in_action = False
        self.drawPage()

    def preset_text(self):
        self.in_action = True
        self.drawPage()
        self.strip.printSigns('MATI', self.display)
        self.in_action = False
        self.drawPage()

######## start the program here ########

stick = Lightstick(_JSON_SETTINGS, _JSON_OPTIONS, _START_PAGE)
stick.drawPage()
while True:
    stick.readKey()

