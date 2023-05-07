#The Pinout Diagram shows the default Pins for SPI0 to be
25 (TX),
24(SCK),
22(CSn),
21 (RX). (SCK),
7(MOSI / TX) and
4 (MISO/ RX).
from machine import SPI,Pin
import uos
import sdcard as SDCard
sd = SDCard.SDCard(SPI(1),Pin(13))
fs = uos.VfsFat(sd)
uos.mount(fs,"/sd")
uos.listdir("/sd")