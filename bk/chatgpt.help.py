import machine
import ssd1306
import ujson

# Set up the buttons
up_button = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
down_button = machine.Pin(1, machine.Pin.IN, machine.Pin.PULL_UP)
left_button = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)
right_button = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_UP)
select_button = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)
cancel_button = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)

# Set up the display
i2c = machine.I2C(scl=machine.Pin(22), sda=machine.Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Load the menu from a JSON file
with open('menu.json', 'r') as f:
    menu = ujson.load(f)

# Initialize the menu position
menu_pos = 0
submenu_pos = 0
current_menu = menu

# Display the menu
def display_menu():
    global current_menu
    oled.fill(0)
    oled.text('Menu:', 0, 0)
    oled.text(current_menu[menu_pos]['title'], 0, 10)
    if 'submenus' in current_menu[menu_pos]:
        oled.text('->', 120, 10)
    oled.show()

# Handle button presses
def handle_buttons():
    global menu_pos, submenu_pos, current_menu
    if up_button.value() == 0:
        if submenu_pos > 0:
            submenu_pos -= 1
        display_menu()
    elif down_button.value() == 0:
        if submenu_pos < len(current_menu[menu_pos]['submenus']) - 1:
            submenu_pos += 1
        display_menu()
    elif left_button.value() == 0:
        if 'parent_menu' in current_menu:
            current_menu = current_menu['parent_menu']
            menu_pos = current_menu.index(current_menu[menu_pos])
            display_menu()
    elif right_button.value() == 0:
        if 'submenus' in current_menu[menu_pos]:
            current_menu = current_menu[menu_pos]['submenus']
            menu_pos = 0
            submenu_pos = 0
            display_menu()
    elif select_button.value() == 0:
        if 'action' in current_menu[menu_pos]:
            current_menu[menu_pos]['action']()
        elif 'submenus' in current_menu[menu_pos]:
            current_menu = current_menu[menu_pos]['submenus']
            menu_pos = 0
            submenu_pos = 0
            display_menu()
    elif cancel_button.value() == 0:
        if 'parent_menu' in current_menu:
            current_menu = current_menu['parent_menu']
            menu_pos = current_menu.index(current_menu[menu_pos])
            display_menu()



with open("image.bmp", "rb") as f:
    f.seek(10)  # skip to the offset value of pixel data
    offset = struct.unpack("<L", f.read(4))[0]
    f.seek(18)  # skip to the width and height values
    width = struct.unpack("<L", f.read(4))[0]
    height = struct.unpack("<L", f.read(4))[0]
    f.seek(offset)  # skip to the pixel data

    # loop through each pixel and display it on the LCD
    for y in range(height):
        for x in range(width):
            pixel = ord(f.read(1))
            color = (pixel << 16) | (pixel << 8) | pixel  # convert monochrome pixel to RGB value
            lcd.pixel(x, y, color)




# Main loop
while True:
    display_menu()
    handle_buttons()