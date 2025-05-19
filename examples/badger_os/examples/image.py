# ICON [[(-15.56, 16.67), (-16.62, 16.55), (-17.87, 16.05), (-18.68, 15.43), (-19.64, 14.01), (-20.0, 12.28), (-20.0, -18.89), (-19.78, -20.32), (-19.21, -21.42), (-18.38, -22.3), (-17.63, -22.82), (-16.61, -23.21), (-15.61, -23.33), (15.56, -23.33), (17.3, -22.98), (18.23, -22.41), (19.24, -21.34), (19.89, -19.89), (20.0, -18.94), (20.0, 12.22), (19.82, 13.49), (19.46, 14.35), (18.63, 15.43), (17.12, 16.39), (15.61, 16.67), (-15.56, 16.67)], [(-15.56, 12.22), (15.56, 12.22), (15.56, -18.89), (-15.56, -18.89), (-15.56, 12.22)], [(-13.33, 7.78), (13.33, 7.78), (5.0, -3.33), (-1.67, 5.56), (-6.67, -1.11), (-13.33, 7.78)]]
# NAME Gallery
# DESC Display your images!

import os
import badger2350
from badger2350 import HEIGHT, WIDTH
import badger_os
import jpegdec
import pngdec
from picovector import ANTIALIAS_BEST, PicoVector, Polygon, Transform


TOTAL_IMAGES = 0


# Turn the act LED on as soon as possible
display = badger2350.Badger2350()
display.led(128)
display.set_update_speed(badger2350.UPDATE_NORMAL)

jpeg = jpegdec.JPEG(display.display)
png = pngdec.PNG(display.display)

# Pico Vector
vector = PicoVector(display.display)
vector.set_antialiasing(ANTIALIAS_BEST)
t = Transform()


# Load images
try:
    IMAGES = [f for f in os.listdir("/images") if f.endswith((".jpg", ".png"))]
    TOTAL_IMAGES = len(IMAGES)
except OSError:
    pass


state = {
    "current_image": 0,
    "show_info": True
}


def show_image(n):
    file = IMAGES[n]
    name, ext = file.split(".")

    try:
        png.open_file("/images/{}".format(file))
        png.decode()
    except (OSError, RuntimeError):
        jpeg.open_file("/images/{}".format(file))
        jpeg.decode()

    if state["show_info"]:

        label = f"{name} ({ext})"
        name_length = display.measure_text(label, 0.5)
        display.set_pen(3)
        text_box = Polygon().rectangle(2, HEIGHT - 23, name_length + 11, 21, (10, 10, 10, 10))
        vector.draw(text_box)
        display.set_pen(0)
        display.text(label, 7, HEIGHT - 15, WIDTH, 0.5)

        for i in range(TOTAL_IMAGES):
            x = WIDTH - 10
            y = int((HEIGHT / 2) - (TOTAL_IMAGES * 10 / 2) + (i * 10))
            display.set_pen(1)
            display.rectangle(x, y, 8, 8)
            if state["current_image"] != i:
                display.set_pen(2)
                display.rectangle(x + 1, y + 1, 6, 6)

    display.update()


if TOTAL_IMAGES == 0:
    raise RuntimeError("To run this demo, create an /images directory on your device and upload some 1bit 264x176 pixel images.")


badger_os.state_load("image", state)

changed = True


while True:
    # Sometimes a button press or hold will keep the system
    # powered *through* HALT, so latch the power back on.
    display.keepalive()

    if display.pressed(badger2350.BUTTON_UP):
        if state["current_image"] > 0:
            state["current_image"] -= 1
            changed = True

    if display.pressed(badger2350.BUTTON_DOWN):
        if state["current_image"] < TOTAL_IMAGES - 1:
            state["current_image"] += 1
            changed = True

    if display.pressed(badger2350.BUTTON_A):
        state["show_info"] = not state["show_info"]
        changed = True

    if changed:
        show_image(state["current_image"])
        badger_os.state_save("image", state)
        changed = False

    # Halt the Badger to save power, it will wake up if any of the front buttons are pressed
    display.halt()
