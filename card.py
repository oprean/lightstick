import gc
from lib.bmp_reader import BMPReader
try:
    import sdcard, machine, SPI, Pin
    import lib.sdcard as sdcard
    import uos as os
    _DEBUG_MODE = False
    _MOUNT = '/sd'
except ImportError or ModuleNotFoundError:
    import os
    _DEBUG_MODE = True
    _MOUNT = ''
class Card:

    def __init__(self, cs_pin, sck_pin, mosi_pin, miso_pin, path = ""):
        self.path = _MOUNT+path
        if (not _DEBUG_MODE):
            spi = machine.SPI(1, 10000, 0, 0, 8, machine.SPI.MSB, Pin(sck_pin), Pin(mosi_pin), Pin(miso_pin))           
            spi.init()  # Ensure right baudrate
            sd = sdcard.SDCard(spi, Pin(cs_pin))  # Compatible with PCB
            #sd = sdcard.SDCard(SPI(1), Pin(cs_pin))  # Compatible with PCB
            vfs = os.VfsFat(sd)
            os.mount(vfs, _MOUNT)
        self.images = self.listdir()

    def listdir(self,path=''):
        images = []
        if path == '':path = self.path
        for file in os.listdir(path):
            if (file.endswith('.bmp')):
                img = BMPReader(path + file)
                info = {
                    'name': file.replace('.bmp',''),
                    'value': file,
                    'width':img.width,
                    'height':img.height
                }
                images.append(info)
        return images

    def getFile(self,id):
        return self.images[id]

    def open(self,file):
        file = self.path + file
        with open(file, "r") as f:
            return f.read()

    def umount(self):
        if (not _DEBUG_MODE):
            os.umount(_MOUNT)    

