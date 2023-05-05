import os
from lib.bmp_reader import BMPReader
try:
    import sdcard, machine
    import lib.sdcard as sdcard
    _DEBUG_MODE = False
except ImportError or ModuleNotFoundError:
    _DEBUG_MODE = True

class Card:

    def __init__(self, spi_pin, cs_pin, fc = "/fc"):
        self.fc = fc
        if (not _DEBUG_MODE):
            spi = machine.SPI(spi_pin)
            spi.init()  # Ensure right baudrate
            sd = sdcard.SDCard(spi, cs_pin)  # Compatible with PCB
            vfs = os.VfsFat(sd)
            os.mount(vfs, self.fc)
        self.images = self.listdir()

    def listdir(self):
        images = []
        for file in os.listdir(self.fc):
            if (file.endswith('.bmp')):
                img = BMPReader(self.fc + file)
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
        file = self.fc + file
        with open(file, "r") as f:
            return f.read()

    def umount(self):
        if (not _DEBUG_MODE):
            os.umount(self.fc)    

