try:
    import machine
    _DEBUG_MODE = False
except ImportError or ModuleNotFoundError:
    import keyboard  
    _DEBUG_MODE = True


class NavKeyboard:
    def __init__(self, up_pin, right_pin, down_pin, left_pin, select_pin):
        if (not _DEBUG_MODE):
            self.up_button = machine.Pin(up_pin, machine.Pin.IN, machine.Pin.PULL_UP)
            self.down_button = machine.Pin(down_pin, machine.Pin.IN, machine.Pin.PULL_UP)
            self.left_button = machine.Pin(left_pin, machine.Pin.IN, machine.Pin.PULL_UP)
            self.right_button = machine.Pin(right_pin, machine.Pin.IN, machine.Pin.PULL_UP)
            self.select_button = machine.Pin(select_pin, machine.Pin.IN, machine.Pin.PULL_UP)
            
    def read_key(self):
        if (_DEBUG_MODE):
            return keyboard.read_key()
        else:
            if (self.up_button.value() == 0):
                return 'up'
            elif (self.right_button.value() == 0):
                return 'right'
            elif (self.down_button.value() == 0):
                return 'down'
            elif (self.left_button.value() == 0):
                return 'left'
            elif (self.select_button.value() == 0):
                return 'enter'
            else:
                return ''