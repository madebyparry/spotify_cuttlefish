# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
import cuttlefish

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# Raspberry Pi pin configuration:
RST = 24
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# 128x32 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Get drawing object to draw on image.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

# Authenticate spotipy
cuttlefish.authenticateSpotipyOauth()

# First define some constants to allow easy resizing of shapes.
padding = 0 
top = padding
bottom = height-padding
x = 0

def splashScreen():
    draw.text((x, top + 8), 'Sportify Cuttlefish', font=font, fill=255)
    draw.text((x, top + 16), 'MadeByParry', font=font, fill=255)
    time.sleep(2)

def displayInfo():
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    track_info = cuttlefish.retCurrentlyPlaying()
    track_time = cuttlefish.printCurrentRuntime()
    draw.text((x, top), track_info[1], font=font, fill=255)
    draw.text((x, top + 8), track_info[0], font=font, fill=255)
    draw.text((x, top + 16), track_info[2], font=font, fill=255)
    draw.text((x, top + 24), 
              track_time, 
              font=font, 
              fill=255
              )
    disp.image(image)
    disp.display()
    time.sleep(1) 

splashScreen()

while True:
    try:
        displayInfo()
    except: 
        print('beep - no track')
        time.sleep(2)
        displayInfo()
else:
    print('boop - done')
