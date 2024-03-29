import gc
import os
import time
import json

try:
    from machine import Pin, I2C
    import micropython
    _DEBUG_MODE = False
except ImportError or ModuleNotFoundError:
    _DEBUG_MODE = True

from oled import OLED
from navkeys import NavKeyboard
from strip import LedPainter
from utils import Utils
from card import Card

###### constants ##########  
_START_PAGE = 'action'
if (not _DEBUG_MODE):
    _JSON_OPTIONS = 'options.json'
    _JSON_SETTINGS = 'settings.json'
    _IMAGES_PATH = '/sd/images/'
else:
    _JSON_OPTIONS = 'C:\Personal\pico\code\Lightstick\options.json'
    _JSON_SETTINGS = 'C:\Personal\pico\code\Lightstick\settings.json'
    _IMAGES_PATH = 'C:\Personal\pico\code\images\\'

_UP = 0
_RIGHT = 1
_DOWN = 2
_LEFT = 3

# "neighbours":["top","right","bottom","left"]

class Lightstick:
    def __init__(self, json_settings_file, json_options_file, selected=_START_PAGE):
        self.selected = selected
        self.in_action = False
        f = open(json_settings_file)
        self.setings = json.load(f)
        self.menu = self.setings['menu']
        f.close()

        f = open(json_options_file)
        self.options = json.load(f)
        f.close()

        for page in self.menu:
            if (page['name'] == self.selected):
                self.page = page

        # init harware

        # SC Card readed
        setings = self.setings['card']
        self.card = Card(setings["cs_pin"], setings["sck_pin"], setings["mosi_pin"], setings["miso_pin"], _IMAGES_PATH)
        self.utils = Utils(self.setings, self.options, self.card)

        # LED STRIP
        setings = self.setings['strip']
        self.strip = LedPainter(setings['num_pixels'], setings['state_machine'], setings['pin'], setings['mode'], setings['delay'], self.options, self.setings)
        
        # OLED Display
        setings = self.setings['oled']
        self.display = OLED(setings['id'], setings['sda_pin'], setings['scl_pin'], self.utils)

        # NAV Keys
        setings = self.setings['navkeys']
        self.wait_key = setings['wait']
        self.keyboard = NavKeyboard(setings["up_pin"], setings["right_pin"], setings["down_pin"], setings["left_pin"], setings["select_pin"], setings["fire_pin"])

        self.strip.initialAnimation()

    def waitKey(self):
        key = ''
        while True:
            if (key != self.keyboard.read_key()): break
        time.sleep(self.wait_key)
        
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
        elif key == 'space':
            self.fire()
        elif key == 'enter' and not self.in_action:
            if 'action' in self.page:
                action = getattr(self, self.page['action'])
                action()
        for page in self.menu:
            if (page['name'] == self.selected):
                self.page = page
        self.drawPage()

    def fire(self):
        id = self.options['action']['value']-1  
        actions = self.utils.getSettingValue('sources.actions')
        action_name = actions[id]['action']
        action = getattr(self, action_name)
        action()

    def drawPage(self):
        self.display.draw(self.page, self.in_action, self.options)

    def update_setting(self):
        if  self.selected in self.options:
            option = self.options[self.selected]
            if 'source' in option:
                if (isinstance(option['source'], list)):
                    source = option['source']
                elif(option['source']=='card'):
                    source = self.card.images
                else:
                    source = self.utils.getSettingValue(option['source'])
                min = 0
                max = len(source)-1
                inc = 1
            else:
                min = option['min']
                max = option['max']
                inc = option['inc']
            self.in_action = True

            self.drawPage()
            while self.in_action == True:
                key = self.keyboard.read_key()
                time.sleep(self.wait_key)
                if (key == 'enter'):
                    self.in_action = False

                    if (_DEBUG_MODE):json_string =  json.dumps(self.options,indent=4)
                    else:json_string =  Utils.json_pretty_print(self.options,indent=4)
                
                    with open(_JSON_OPTIONS, 'w') as f:
                         f.write(json_string)

                    if (self.selected == 'brightness'):
                        if (not _DEBUG_MODE):
                            self.strip.strip.brightness(option['value'])
                    break
                elif (key == 'right'):
                    if (option['value']>=max):option['value'] = min-inc
                    option["value"] += inc
                elif (key == 'left'):
                    if (option['value']<=min):option['value'] = max+inc
                    option["value"] += -inc
                self.options[self.selected]['value'] = option['value']
                self.drawPage()

############# PRESETS ###############

    def preset_gradient(self):
        self.in_action = True
        self.drawPage()
        self.strip.gradient(self.options['gradient_color1']['value'], self.options['gradient_color2']['value'])
        self.waitKey()
        self.strip.clear()
        self.in_action = False
        self.drawPage()

    def preset_fire(self):
        self.in_action = True
        self.drawPage()
        key = ''
        self.strip.upper_fire = 15
        while True:
            self.strip.fire()
            key = self.keyboard.read_key()
            time.sleep(self.wait_key/10)
            if key != '': break        
        self.strip.clear()
        self.in_action = False
        self.drawPage()

    def preset_rainbow(self):
        self.in_action = True
        self.drawPage()
        self.strip.rainbow()
        self.waitKey()        
        self.strip.clear()
        self.in_action = False
        self.drawPage()

    def preset_text(self):
        self.in_action = True
        id = self.utils.getOptionValue('text')
        id = id['value']-1
        text = self.utils.getSettingValue('sources.texts')
        text = text[id]['value']
        self.drawPage()
        self.strip.printSigns(text, self.display)
        self.in_action = False
        self.drawPage()

    def preset_image(self, file = ''):
        self.in_action = True
        if (file == ''):
            id = self.utils.getOptionValue('image')
            id = id['value']-1
            file = self.card.getFile(id)
            print(file);
        self.drawPage()
        self.strip.image(_IMAGES_PATH + file['value'])
        self.in_action = False
        #self.drawPage()

######## start the program here ########

stick = Lightstick(_JSON_SETTINGS, _JSON_OPTIONS, _START_PAGE)
#https://docs.micropython.org/en/latest/reference/constrained.html
#stick.preset_image('matei_oprean.bmp')
#print(stick.card.listdir(_IMAGES_PATH))

stick.drawPage()
while True:
    stick.readKey()

