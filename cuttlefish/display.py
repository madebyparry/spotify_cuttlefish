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
from cuttlefish import currentlyPlaying, printCurrentlyPlaying, currentRuntime, relatedArtists, authenticateSpotipyOauth, playPauseMusic, nextTrack
from gpiozero import MCP3008, LED, Button
from threading import Thread
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# Raspberry Pi pin configuration:
RST = 24
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

#set potentiometer pin
pot = MCP3008(0)

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
authenticateSpotipyOauth()

# First define some constants to allow easy resizing of shapes.
padding = 0 
top = padding
bottom = height-padding
x = 0

#buttons 
led_one = LED(26)
btn_one = Button(19)
btn_two = Button(13)
btn_thr = Button(6)
btn_for = Button(5)

#button controls
def blink(num, t):
        i = 0
        while i < num:
                led_one.on()
                time.sleep(t)
                led_one.off()
                time.sleep(t)
                i = i + 1

def playback():
    playPauseMusic()
    blink(1, 0.5)

def playing():
    currentlyPlaying()
    printCurrentlyPlaying()
    blink(3, 0.2)

def nextButton():
    nextTrack()
    blink(2, 0.02)

def related():
    blink(5, 0.1)
    relatedArtists()

def displayInfo():
    vol = round(pot.value, 1) * 10
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    track_info = currentlyPlaying()
    track_time = currentRuntime()
    draw.text((x, top), track_info['track_name'], font=font, fill=255)
    draw.text((x, top + 8), track_info['artist_name'], font=font, fill=255)
    draw.text((x, top + 16), track_info['album_name'], font=font, fill=255)
    draw.text((x, top + 24), 'vol:' + ('#' * int(vol)), font=font, fill=255)
    disp.image(image)
    disp.display()

def buttonDaemon():
    while True:
        if btn_one.is_pressed:
            playback()
        if btn_two.is_pressed:
            playing()
        if btn_thr.is_pressed:
            nextButton()
        if btn_for.is_pressed:
            related()
        time.sleep(0.1) 

daemon = Thread(target=buttonDaemon, daemon=True, name='Button Monitor')
daemon.start()

while True:
    try:
        displayInfo()
        time.sleep(0.5) 
    except: 
        time.sleep(2)
        displayInfo()
else:
        print('boop - done')
