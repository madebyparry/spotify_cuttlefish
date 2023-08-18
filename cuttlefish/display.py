# 
#   Button pinout 
#     (Based on pin location)[GPIO Number]
#   Screen:
#       VCC - (1)[3v3]
#       GRND - (6)[GRND]
#       SDA - (5)[3]
#       SCL - (7)[4]
#
#   MCP3008:
#       13 - (23)[11]
#       12 - (21)[9]
#       11 - (19)[10]
#       10 - (24)[8]
#
#   Others:
#       LED - (37)[26]
#       Bn1 - (35)[19]
#       Bn2 - (33)[13]
#       Bn3 - (31)[6]
#       Bn4 - (29)[5]
#       Bn5 - (36)[16]
#

import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
from cuttlefish import setEnvVars, currentlyPlaying, printCurrentlyPlaying, currentRuntime, relatedArtists, playPauseMusic, nextTrack
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
setEnvVars()

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
btn_fiv = Button(16)

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

def wikiTime():
     blink(4, 0.3)
     printWikiResults()

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
        if btn_fiv.is_pressed:
            wikiTime()
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
