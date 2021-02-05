#!/usr/bin/env python3
# rpi_ws281x library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.

import sys
import time
from rpi_ws281x import *
import argparse
from color_dict import COLORS
# LED strip configuration:
LED_COUNT      = 300      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

def eprint(*args):
    print(*args, file=sys.stderr)

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, color)
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, wheel((i+j) % 255))
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)


def pattern(strip):
    colors = [Color(255, 0, 0), Color(0, 255, 0), Color(0, 0, 255)]
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, colors[i%3])
    strip.show()

def single_color(strip, color):
    """Draw rainbow that fades across all pixels at once."""
    # think of 0-255 as affecting intensity as well
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()

def test_brightness(strip):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0,0, strip.numPixels()//255*(strip.numPixels() - i)))
    strip.show()

def apply_brightness(rgba):
    """
    Turn an rgba value into rgb. The Color obj doesn't take a brightness value.
    Instead, a lower value is a dimmer color. Thus, we can decrease the r, g,
    and b values by a factor to simulate alpha.
    """
    print(rgba)
    if type(rgba[3]) == float:
        factor = rgba[3]
    else:
        factor = rgba[3] / 255 
    ret = list(map(lambda x: int(x * factor), rgba[:3]))
    print(ret)
    return ret

def hex_to_rgb(hexcode):
    """
    Convert a hex value to an rgb value. Alpha value can be included.
    e.g.: 0x112233, 0x11223344
    """
    if hexcode[0] == '#':
        hexcode = hexcode[1:]
    print('incoming hex: ', hexcode)
    hexcode = int(hexcode, 16)
    rgba = [0xFF] * 4
    if hexcode & 0xFF000000:  # if there's a alpha value
        for i in range(4):
            offset = 24 - (i*8)
            rgba[i] = (hexcode & (0xFF << offset)) >> offset
    else:  # no alpha value
        for i in range(3):
            offset = 16 - (i*8)
            rgba[i] = (hexcode & (0xFF << offset)) >> offset
    # apply alpha to colors
    return apply_brightness(rgba)

def handle_color_arg(strip, args):
    """
    handle the color choice. The color choice can be:
    - a string representing the name of a color. This should be compared to the internal dictionary
    - 3 numbers representing an RGB value
    """
    num_args = len(args)
    color = None
    if num_args == 1:
        color = Color(*hex_to_rgb(args[0])) 
    elif num_args == 3:
        color = Color(*map(int, args))
    elif num_args == 4:
        color = Color(*apply_brightness(list(map(float,args))))
    else:
        eprint('Number of arguments not recognized')
        exit(-1)
    single_color(strip, color)


# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    """
    options:
        - choose a specific color
        - choose a set of colors to repeat
        - option to fade between colors
        - option to wipe between colors
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--clear', action='store_true', help='clear the display on exit')
    parser.add_argument('-c', '--color', nargs='+', help='specify a specific RGB color e.g. 255 255 255')
    parser.add_argument('-C', '--name_color')
    parser.add_argument('--off', action='store_true', help='turn lights off')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    if args.off:
        single_color(strip, Color(0, 0, 0))
        exit()
    try:
        if args.color:
            handle_color_arg(strip, args.color)
        elif args.name_color:
            if args.name_color not in COLORS:
                eprint(f'color ${args[0]} not recognized')
                exit()
            single_color(strip, Color(*hex_to_rgb(COLORS[args.name_color])))
        else:
            # rainbow(strip, iterations=100)
            test_brightness(strip)

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0,0,0), 10)
