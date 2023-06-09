import os
try:
    from machine import Pin, I2C
    import lib.ssd1306 as ssd1306
    _DEBUG_MODE = False
except ImportError or ModuleNotFoundError:
    _DEBUG_MODE = True

_UP = 0
_RIGHT = 1
_DOWN = 2
_LEFT = 3

class OLED:
    def __init__(self, id, sda_pin, scl_pin, utils = False):
        if (not _DEBUG_MODE):
            i2c = I2C(id, sda=Pin(sda_pin), scl=Pin(scl_pin))
            self.lcd = ssd1306.SSD1306_I2C(128, 64, i2c)

        self.page = False
        self.in_action = False
        self.options = False
        self.utils = utils

    def drawPageHeader(self):
        udarrows = ''
        lrarrows = ''
        if (self.page['neighbours'][_UP]!=''): 
            if (_DEBUG_MODE):udarrows +='\u25B2'
            else:self.lcd.hline(1,1,128,1)
        if (self.page['neighbours'][_DOWN]!=''): 
            if (_DEBUG_MODE):udarrows +='\u25BC'
            else:self.lcd.hline(1,11,128,1)
        if (self.page['neighbours'][_LEFT]!=''): 
            if (_DEBUG_MODE):lrarrows +='\u25C4'
            else:self.lcd.vline(1,1,11,1)            
        if (self.page['neighbours'][_RIGHT]!=''): 
            if (_DEBUG_MODE):lrarrows +='\u25BA'
            else:self.lcd.vline(127,1,11,1)


        if (_DEBUG_MODE):print(lrarrows+' '+self.page['label']+' '+udarrows)
        else:self.lcd.text(self.page['label'], 2, 3)

    def drawPageContent(self):
        if (self.page['type'] == 'static'):            
            if (_DEBUG_MODE):print(self.page['content'])
            else:self.lcd.text(self.page['content'], 2, 14)
        elif (self.page['type'] == 'option' and self.page['name'] in self.options):

            if 'source' in self.options[self.page['name']]:
                source = self.utils.getSettingValue(self.options[self.page['name']]['source'])
                label = source[self.options[self.page['name']]['value']-1]['name']
            else:
                label = self.options[self.page['name']]['value']
                
            if (self.in_action):
                if (_DEBUG_MODE):
                    print(self.options[self.page['name']])
                    print(label)
                else:
                    self.lcd.rect(10, 24, 108, 24, 1)
                    self.lcd.fill_rect(10, 24, int(self.options[self.page['name']]['value']),24,1)
                    self.lcd.text('Value: ' + str(label), 12, 34)
            else:
                if (_DEBUG_MODE):
                    print(self.options[self.page['name']])
                    print(label)
                else:self.lcd.text('Value: ' + str(label), 12, 34)
        elif (self.page['type'] == 'preset'):
            if (_DEBUG_MODE):print(self.page['content'])
            else:
                self.lcd.text(self.page['content'], 2, 24)
                if (self.in_action):
                    self.lcd.rect(25, 40, 60, 14, 1)
                    self.lcd.text('Action!', 28, 43)

    def text(self, text):
        self.lcd.fill(0)
        self.lcd.text(text, 22, 34)
        self.lcd.show()
        
    def draw(self, page, in_action, options):
            self.page = page
            self.in_action = in_action
            self.options = options
            if (_DEBUG_MODE):os.system('cls')
            else:self.lcd.fill(0)
            self.drawPageHeader()
            self.drawPageContent()
            if (not _DEBUG_MODE):self.lcd.show()      
