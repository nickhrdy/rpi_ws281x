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
    """Print to stderr"""
    print(*args, file=sys.stderr)

def pattern(strip):
    colors = [Color(255, 0, 0), Color(0, 255, 0), Color(0, 0, 255)]
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, colors[i%3])
    strip.show()

def single_color(strip, color):
    """Make the entire strip a single color"""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()

def apply_brightness(rgba):
    """
    Turn an rgba value into rgb. The Color obj doesn't take a brightness value.
    Instead, a lower value is a dimmer color. Thus, we can decrease the r, g,
    and b values by a factor to simulate alpha.
    """
    if type(rgba[3]) == float:
        factor = rgba[3]
    else:
        factor = rgba[3] / 255 
    ret = list(map(lambda x: int(x * factor), rgba[:3]))
    return ret

def hex_to_rgb(hexcode):
    """
    Convert a hex value to an rgb value. Alpha value can be included.
    e.g.: 0x112233, 0x11223344
    """
    if hexcode[0] == '#':
        hexcode = hexcode[1:]
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
    return rgba

def handle_color_arg(args):
    """
    handle the color choice. The color choice can be:
    - a string representing the name of a color. This should be compared to the internal dictionary
    - 3 numbers representing an RGB value
    """
    color = None
    num_args = len(args)
    if type(args) == str:
        color = hex_to_rgb(args) 
    elif num_args == 1:
        color = hex_to_rgb(args[0]) 
    elif num_args == 3:
        color = list(map(int, args))
        color.append(1.0)
    elif num_args == 4:
        color = list(map(float,args))
    else:
        eprint('Number of arguments not recognized')
        exit(-1)
    return color

# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    """
    options:
        - (DONE) choose a specific color
        - choose a set of colors to repeat
        - option to fade between colors
        - option to wipe between colors
    """
    parser = argparse.ArgumentParser()
    #parser.add_argument('-q', '--clear', action='store_true', help='clear the display on exit')
    parser.add_argument('-c', '--color', nargs='+', help='specify a specific color. color formats can be RGB/RGBA or hex code (e.g., "255 0 0", "255, 0, 0, 0.5", "#fe3211", "#442ab308")')
    parser.add_argument('-C', '--name_color', type=str, help='specify a color by name. A dictionary of available names can be found in color_dict.py')
    parser.add_argument('-b', '--brightness', type=float, help='brightness of lights (0.0-1.0). This will overwrite any brightness value implies by the other flags')
    parser.add_argument('-q', '--quit', action='store_true', help='turn lights off')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    if args.quit:
        single_color(strip, Color(0, 0, 0))
        exit()
    try:
        if args.color:
            rgba_vals = handle_color_arg(args.color)
        elif args.name_color:
            key = args.name_color.lower()
            if key not in COLORS:
                eprint(f'color "{key}" not recognized')
                exit()
            print(COLORS[key])
            rgba_vals = handle_color_arg(COLORS[key])

        if args.brightness:
            # overwrite current brightness value
            rgba_vals[3] = args.brightness
    
        rgb_vals = apply_brightness(rgba_vals)
        single_color(strip, Color(*rgb_vals))

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0,0,0), 10)
