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

class ColorContainer:
    """Collection of functions to manage different color representations."""
    red = 0
    green = 0
    blue = 0
    brightness = 1.0

    def _convert_hexcode(self, hexcode):
        """
        Converts hexcode into rgba representation.
        Hexcode can be #112233 or #11223344
        """
        if hexcode[0] == '#':
            hexcode = hexcode[1:]
        hexcode = int(hexcode, 16)
        if hexcode & (0xFF << 24): # has alpha value
            self.red = (hexcode & (0xFF << 24)) >> 24
            self.green = (hexcode & (0xFF << 16)) >> 16
            self.blue = (hexcode & (0xFF << 8)) >> 8
            self.brightness = hexcode & 0xFF
        else: # no alpha value
            self.red = (hexcode & (0xFF << 16)) >> 16
            self.green = (hexcode & (0xFF << 8)) >> 8
            self.blue = hexcode & 0xFF
            self.brightness = 1.0

    def _apply_brightness(self):
        """
        Adjust RGB values by brightness factor. The LEDs can only interpret
        RGB value, so the brightness has to be applied before being sent
        to the LEDs.

        Brightness values can either be in the float range [0, 1.0] or
        int range [0, 255]
        """
        if type(self.brightness) == float:
            factor = self.brightness
        else:
            factor = self.brightness / 255
        # not sure why I get a type error if I don't cast them
        # to a float before the map
        vals = [float(x) for x in [self.red, self.green, self.blue]]
        return list(map(lambda x: int(x*factor), vals))
    
    def _set_color_array(self, arr):
        """Helper method for parsing an array of rgb(a) vals"""
        self.red=arr[0]
        self.green=arr[1]
        self.blue=arr[2]
        if len(arr) == 4:
            self.brightness = arr[3]

    def __init__(self, *args):
        """
        Create a color container. Input can be an array representing an
        rgb(a) value (e.g., [255, 0, 0, 0.5]) or a hexcode (e.g., #ff0000)
        """

        if len(args) in [3, 4]:
            self._set_color_array(args) 
        else:
            self._convert_hexcode(args[0])

    def get_color(self):
        """Get current color an int value"""
        return Color(*self._apply_brightness())

    def __repr__(self):
        return f'Color<({self.red}, {self.blue}, {self.green}, {self.brightness})>'

def eprint(*args):
    """Print to stderr"""
    print(*args, file=sys.stderr)

def pattern(strip, colors):
    """Alternate a series of colors down the length of a strip"""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, colors[i % len(colors)].get_color())
    strip.show()

def single_color(strip, color):
    """Make the entire strip a single color"""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color.get_color())
    strip.show()

def fade(strip, colors, delay=0):
    """Fade in and out between a series of colors"""
    # Note: delay in ms

    # Create array of brightness steps
    bright_vals = [i for i in range(100)]
    bright_vals.extend(bright_vals[::-1])
    bright_vals = list(map(lambda x: x/100.0, bright_vals))

    num_colors = len(colors)
    idx = 0
    while True:
        curr_color = colors[idx]
        for brightness in bright_vals:
            curr_color.brightness = brightness
            for i in range(0, strip.numPixels()):
                strip.setPixelColor(i, curr_color.get_color())
            strip.show()
            time.sleep(delay/100)
        idx = (idx + 1) % num_colors

# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    """
    options:
        - (DONE) choose a specific color
        - choose a set of colors to repeat
        - (DONE) option to fade between colors
        - option to wipe between colors
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--erase', action='store_true', help='clear the display on exit')
    parser.add_argument('-c', '--color', nargs='+', help='specify a specific color. color formats can be RGB/RGBA or hex code (e.g., "255 0 0", "255, 0, 0, 0.5", "#fe3211", "#442ab308")')
    parser.add_argument('-C', '--name_color', type=str, help='specify a color by name. A dictionary of available names can be found in color_dict.py')
    parser.add_argument('-b', '--brightness', type=float, help='brightness of lights (0.0-1.0). This will overwrite any brightness value implies by the other flags')
    parser.add_argument('-q', '--quit', action='store_true', help='turn lights off')
    parser.add_argument('-d', '--delay', type=int, help='set the delay. Only applies to some features')
    parser.add_argument('-p', '--pattern', nargs='+', help='repeat a series of color along a strip')
    parser.add_argument('-f', '--fade', nargs='+', help='fade between a series of specified colors')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    if args.quit:
        single_color(strip, ColorContainer(0, 0, 0))
        exit()
    try:
        if args.pattern:
            for idx, c in enumerate(args.pattern):
                if c in COLORS:
                    args.pattern[idx] = COLORS[c]
            pattern(strip, [ ColorContainer(c) for c in args.pattern ])
        elif args.fade:
            for idx, c in enumerate(args.fade):
                if c in COLORS:
                    args.fade[idx] = COLORS[c]
            fade(strip, [ ColorContainer(x) for x in args.fade ], delay = args.delay or 0)
        else:
            if args.color:
                color = ColorContainer(args.color)
            elif args.name_color:
                key = args.name_color.lower()
                if key not in COLORS:
                    eprint(f'color "{key}" not recognized')
                    exit()
                color = ColorContainer(COLORS[key])
            single_color(strip, color)

    except KeyboardInterrupt:
        if args.erase:
            single_color(strip, ColorContainer(0, 0, 0))
