# ICON [[(-2.01, 8.0), (1.99, 8.0), (1.99, -4.0), (-2.01, -4.0), (-2.01, 8.0)], [(-0.01, -8.0), (0.81, -8.16), (1.68, -8.91), (1.99, -9.86), (1.72, -11.01), (1.14, -11.63), (0.33, -11.98), (-0.31, -11.98), (-1.08, -11.71), (-1.55, -11.29), (-1.97, -10.4), (-1.85, -9.19), (-1.49, -8.59), (-0.71, -8.12), (-0.06, -8.0)], [(-0.01, 18.0), (-2.77, 17.82), (-5.22, 17.33), (-6.81, 16.84), (-9.0, 15.88), (-10.82, 14.83), (-12.37, 13.73), (-13.38, 12.88), (-14.8, 11.47), (-16.53, 9.28), (-17.71, 7.33), (-18.44, 5.84), (-18.93, 4.56), (-19.44, 2.82), (-19.69, 1.62), (-19.93, -0.24), (-19.98, -3.03), (-19.82, -4.82), (-19.36, -7.14), (-18.78, -8.99), (-18.18, -10.41), (-16.87, -12.77), (-15.61, -14.52), (-14.53, -15.77), (-13.03, -17.19), (-11.75, -18.19), (-9.49, -19.6), (-7.63, -20.48), (-5.31, -21.29), (-2.8, -21.81), (-1.17, -21.97), (0.56, -22.0), (2.17, -21.89), (4.17, -21.57), (5.78, -21.15), (6.98, -20.74), (8.54, -20.07), (10.61, -18.95), (12.5, -17.62), (14.56, -15.73), (15.71, -14.38), (16.82, -12.81), (18.11, -10.45), (18.75, -8.94), (19.3, -7.26), (19.84, -4.56), (19.98, -2.76), (19.98, -1.18), (19.8, 0.82), (19.39, 2.89), (18.67, 5.12), (17.97, 6.73), (16.56, 9.2), (15.45, 10.7), (13.58, 12.69), (11.88, 14.09), (10.45, 15.06), (9.16, 15.79), (6.7, 16.87), (5.01, 17.38), (2.25, 17.88), (0.04, 18.0)], [(-0.01, 14.0), (1.92, 13.89), (4.04, 13.53), (6.12, 12.86), (7.5, 12.21), (8.55, 11.61), (9.86, 10.67), (11.86, 8.81), (13.1, 7.28), (14.15, 5.61), (14.75, 4.36), (15.29, 2.88), (15.79, 0.68), (15.96, -0.91), (15.96, -3.16), (15.72, -5.08), (15.17, -7.27), (14.67, -8.56), (13.98, -9.93), (12.87, -11.61), (11.38, -13.32), (9.85, -14.68), (8.89, -15.38), (7.49, -16.22), (5.15, -17.22), (3.7, -17.61), (1.72, -17.92), (0.3, -18.0), (-1.89, -17.9), (-4.1, -17.52), (-5.31, -17.17), (-7.19, -16.38), (-8.13, -15.88), (-9.61, -14.88), (-10.93, -13.76), (-12.29, -12.34), (-13.3, -11.02), (-14.5, -8.96), (-15.22, -7.16), (-15.61, -5.71), (-15.89, -4.07), (-15.99, -1.35), (-15.76, 0.93), (-15.4, 2.54), (-14.53, 4.89), (-13.63, 6.52), (-12.25, 8.38), (-10.86, 9.82), (-9.67, 10.82), (-8.31, 11.75), (-6.16, 12.84), (-5.16, 13.21), (-2.83, 13.77), (-1.35, 13.95), (-0.06, 14.0)]]
# NAME Info
# DESC Badger 2350 Specification & Info

import badger2350
from badger2350 import WIDTH, HEIGHT
import version
from picovector import ANTIALIAS_BEST, PicoVector, Polygon, Transform

TEXT_SIZE = 1
LINE_HEIGHT = 15

version = version.BUILD

display = badger2350.Badger2350()
display.led(128)

# Pico Vector
vector = PicoVector(display.display)
vector.set_antialiasing(ANTIALIAS_BEST)
t = Transform()

TITLE_BAR = Polygon()
TITLE_BAR.rectangle(2, 2, 260, 16, (8, 8, 8, 8))
TITLE_BAR.circle(253, 10, 4)

TEXT_BOX = Polygon()
TEXT_BOX.rectangle(2, 30, 260, 125, (8, 8, 8, 8))

# Clear to white
display.set_pen(15)
display.clear()

display.set_font("bitmap8")
display.set_pen(0)
vector.draw(TITLE_BAR)
display.set_pen(15)
display.text("badgerOS", 7, 6, WIDTH, 1.0)
display.text("info", WIDTH - 40, 6, WIDTH, 1)

display.set_pen(2)
vector.draw(TEXT_BOX)

display.set_pen(1)

y = 32 + int(LINE_HEIGHT / 2)

display.text("Made by Pimoroni, powered by MicroPython", 5, y, WIDTH, TEXT_SIZE)
y += LINE_HEIGHT
display.text("Dual-core RP2350, Up to 150MHz with 520KB of SRAM", 5, y, WIDTH, TEXT_SIZE)
y += LINE_HEIGHT
display.text("4MB of QSPI flash", 5, y, WIDTH, TEXT_SIZE)
y += LINE_HEIGHT
display.text("264x176 pixel Black/White e-Ink", 5, y, WIDTH, TEXT_SIZE)
y += LINE_HEIGHT
display.text("For more info:", 5, y, WIDTH, TEXT_SIZE)
y += LINE_HEIGHT
display.text("https://pimoroni.com/badger2350", 5, y, WIDTH, TEXT_SIZE)
y += LINE_HEIGHT
display.text(f"\nBadger OS {version}", 5, y, WIDTH, TEXT_SIZE)

display.update()

# Call halt in a loop, on battery this switches off power.
# On USB, the app will exit when A+C is pressed because the launcher picks that up.

while True:
    display.keepalive()
    display.halt()
