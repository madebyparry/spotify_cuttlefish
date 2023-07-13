#!/usr/bin/env/ python3

from gpiozero import LED, Button, PWMLED, MCP3008
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
from time import sleep
from signal import pause
from cuttlefish import similarArtists, currentlyPlaying, playPauseMusic, nextTrack, authenticateSpotipyCreds, currentRuntime

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

#
# Current GPIO Configuration
#   LED
#   Playback button
#   Related Button
#   Skip button
#   Info button
#
#   --TODO--
#   Volume Knob
#   Heart button
#
                                      
led_one = LED(37)
btn_one = Button(29)
btn_two = Button(31)
btn_thr = Button(33)
btn_for = Button(35)
pot = MCP3008(0)

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
padding = 0 
top = padding
bottom = height-padding
x = 0



def blink(num, time):
        i = 0
        while i < num:
                led_one.on()
                sleep(time)
                led_one.off()
                sleep(time)
                i = i + 1

def playback():
        playPauseMusic()
        blink(1, 0.5)

def playing():
        currentlyPlaying()
        blink(3, 0.2)
def next():
        nextTrack()
        indicatorOne(3, 0.05)

def related():
    similarArtists()
    indicatorOne(5, 0.25)

def indicatorOne(c, t):
        led_one.on()
        i = 1
        v = 0.5
        while i < c:
            led_one.on()
            sleep(t)
            led_one.on()
            sleep(t)
            i = i + 1
        print("button pressed")
        led_one.value = 0  

def displayInfo():
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    track_info = currentlyPlaying()
    track_time = currentRuntime()
    draw.text((x, top), track_info['track_name'], font=font, fill=255)
    draw.text((x, top + 8), track_info['artist_name'], font=font, fill=255)
    draw.text((x, top + 16), track_info['album_name'], font=font, fill=255)
    draw.text((x, top + 24), 
              track_time, 
              font=font, 
              fill=255
              )
    disp.image(image)
    disp.display()

authenticateSpotipyCreds()
blink(3, 0.2)
print("Cuttlefish Player Active.")
while True:
        try:
                displayInfo()
                btn_one.when_pressed = playback
                btn_two.when_pressed = playing
                btn_thr.when_pressed = next
                btn_for.when_pressed = related
                sleep(1) 
                pause()
        finally:
                print("goodbye.")
                pass
