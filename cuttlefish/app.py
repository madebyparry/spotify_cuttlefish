#!/usr/bin/env/ python3

from gpiozero import LED, Button, PWMLED
from time import sleep
from signal import pause
from cuttlefish import similarArtists, currentlyPlaying, playPauseMusic, nextTrack, authenticateSpotipyCreds

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
                                      
led_one = LED(2)
btn_one = Button(4)
btn_two = Button(17)
btn_thr = Button(27)
btn_for = Button(22)

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
authenticateSpotipyCreds()
blink(3, 0.2)
print("Cuttlefish Player Active.")
try:
        btn_one.when_pressed = playback
        btn_two.when_pressed = playing
        btn_thr.when_pressed = next
        btn_for.when_pressed = related
        pause()
finally:
    print("goodbye.")
    pass
