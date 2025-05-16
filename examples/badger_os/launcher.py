import gc
import os
import time
import math
import badger2350
import badger_os
import pngdec
import jpegdec
from picovector import ANTIALIAS_BEST, PicoVector, Polygon, Transform

DEFAULT_ICON = [
        [(-10.0, 12.5), (10.0, 12.5), (10.0, 7.5), (-10.0, 7.5), (-10.0, 12.5)],
        [(-10.0, 2.5), (10.0, 2.5), (10.0, -2.5), (-10.0, -2.5), (-10.0, 2.5)],
        [
            (-15.0, 22.5),
            (-16.43, 22.31),
            (-17.75, 21.71),
            (-18.52, 21.11),
            (-19.47, 19.78),
            (-19.92, 18.46),
            (-20.0, 17.56),
            (-20.0, -22.5),
            (-19.77, -24.05),
            (-18.82, -25.73),
            (-17.79, -26.64),
            (-16.69, -27.21),
            (-15.06, -27.5),
            (5.0, -27.5),
            (20.0, -12.5),
            (20.0, 17.5),
            (19.77, 19.04),
            (19.36, 19.95),
            (18.55, 21.02),
            (17.74, 21.68),
            (16.7, 22.21),
            (15.06, 22.5),
            (-15.0, 22.5),
        ],
        [
            (2.5, -10.0),
            (2.5, -22.5),
            (-15.0, -22.5),
            (-15.0, 17.5),
            (15.0, 17.5),
            (15.0, -10.0),
            (2.5, -10.0),
        ]
    ]

APP_DIR = "/examples"
FONT_SIZE = 1

changed = False
exited_to_launcher = False
woken_by_button = badger2350.woken_by_button()  # Must be done before we clear_pressed_to_wake


if badger2350.pressed_to_wake(badger2350.BUTTON_A) and badger2350.pressed_to_wake(badger2350.BUTTON_C):
    # Pressing A and C together at start quits app
    exited_to_launcher = badger_os.state_clear_running()
    badger2350.reset_pressed_to_wake()
else:
    # Otherwise restore previously running app
    badger_os.state_launch()


display = badger2350.Badger2350()
display.set_font("bitmap8")
display.led(0)

# Pico Vector
vector = PicoVector(display.display)
vector.set_antialiasing(ANTIALIAS_BEST)
t = Transform()

TITLE_BAR = Polygon()
TITLE_BAR.rectangle(2, 2, 260, 16, (8, 8, 8, 8))
TITLE_BAR.circle(253, 10, 4)

SELECTED_BORDER = Polygon()
SELECTED_BORDER.rectangle(0, 0, 90, 90, (10, 10, 10, 10), 5)

png = pngdec.PNG(display.display)
jpeg = jpegdec.JPEG(display.display)

state = {
    "page": 0,
    "running": "launcher"
}

badger_os.state_load("launcher", state)

examples = [x[:-3] for x in os.listdir(APP_DIR) if x.endswith(".py")]

# Page layout
centers = [[45, 52], [126, 52], [209, 52], [45, 130], [126, 130], [209, 130]]

MAX_PAGE = math.ceil(len(examples) / 6)
MAX_PER_ROW = 3
MAX_PER_PAGE = MAX_PER_ROW * 2

WIDTH = 264

# index for the currently selected file on the page
selected_file = 1

# Number of icons on the current page
icons_total = 0


def map_value(input, in_min, in_max, out_min, out_max):
    return (((input - in_min) * (out_max - out_min)) / (in_max - in_min)) + out_min


def draw_disk_usage(x):
    _, f_used, _ = badger_os.get_disk_usage()

    display.set_pen(15)
    display.image(
        bytearray(
            (
                0b00000000,
                0b00111100,
                0b00111100,
                0b00111100,
                0b00111000,
                0b00000000,
                0b00000000,
                0b00000001,
            )
        ),
        8,
        8,
        x,
        6,
    )
    display.rectangle(x + 10, 5, 45, 10)
    display.set_pen(0)
    display.rectangle(x + 11, 6, 43, 8)
    display.set_pen(15)
    display.rectangle(x + 12, 7, int(41 / 100.0 * f_used), 6)
    #display.text("{:.2f}%".format(f_used), x + 90, 6, WIDTH, 1.0)

def render():
    global icons_total
    global selected_file

    display.set_pen(display.create_pen(200, 200, 200))
    display.clear()
    display.set_pen(0)

    icons_total = min(6, len(examples[(state["page"] * 6):]))

    for i in range(icons_total):
        x = centers[i][0]
        y = centers[i][1]

        label = examples[i + (state["page"] * 6)]
        file = f"{APP_DIR}/{label}.py"

        name = label
        icon = Polygon()

        with open(file) as f:
            header = [f.readline().strip() for _ in range(3)]

            for line in header:
                if line.startswith("# ICON "):
                    try:
                        for path in eval(line[7:]):
                            icon.path(*path)

                    except:  # noqa: E722 - eval could barf up all kinds of nonsense
                        pass
                else:
                    # If there's no icon in the file header we'll use the default.
                    for path in DEFAULT_ICON:
                        icon.path(*path)

                if line.startswith("# NAME "):
                    name = line[7:]

        vector.set_transform(t)
        t.translate(x, y)
        t.scale(0.8, 0.8)
        vector.draw(icon)

        # Snap to the last icon if the position isn't available.
        selected_file = min(selected_file, icons_total - 1)

        if selected_file == i:
            display.set_pen(1)
            t.translate(-45, -36)
            t.scale(1.0, 1.0)
            vector.draw(SELECTED_BORDER)
        t.reset()

        display.set_pen(0)
        w = display.measure_text(name, FONT_SIZE)
        display.text(name, int(x - (w / 2)), y + 27, WIDTH, FONT_SIZE)

    for i in range(MAX_PAGE):
        x = 253
        y = int((176 / 2) - (MAX_PAGE * 10 / 2) + (i * 10))
        display.set_pen(0)
        display.rectangle(x, y, 8, 8)
        if state["page"] != i:
            display.set_pen(3)
            display.rectangle(x + 1, y + 1, 6, 6)

    display.set_pen(0)
    vector.draw(TITLE_BAR)

    draw_disk_usage(100)

    display.set_pen(3)
    display.text("badgerOS", 7, 6, WIDTH, 1.0)

    display.update()


def wait_for_user_to_release_buttons():
    while display.pressed_any():
        time.sleep(0.01)


def launch_example(index):
    wait_for_user_to_release_buttons()

    file = examples[index]
    file = f"{APP_DIR}/{file}"

    for k in locals().keys():
        if k not in ("gc", "file", "badger_os"):
            del locals()[k]

    gc.collect()

    badger_os.launch(file)



def button(pin):
    global changed
    global selected_file
    global icons_total
    changed = True

    if pin == badger2350.BUTTON_A:
        if (selected_file % MAX_PER_ROW) > 0:
            selected_file -= 1

    if pin == badger2350.BUTTON_B:
        launch_example((state["page"] * MAX_PER_PAGE) + selected_file)

    if pin == badger2350.BUTTON_C:
        if (selected_file % MAX_PER_ROW) < MAX_PER_ROW - 1:
            selected_file += 1

    if pin == badger2350.BUTTON_UP:
        if selected_file >= MAX_PER_ROW:
            selected_file -= MAX_PER_ROW
        else:
            state["page"] = (state["page"] - 1) % MAX_PAGE
            selected_file += MAX_PER_ROW

    if pin == badger2350.BUTTON_DOWN:
        if selected_file < MAX_PER_ROW and icons_total > MAX_PER_ROW:
            selected_file += MAX_PER_ROW
        elif selected_file >= MAX_PER_ROW or icons_total < MAX_PER_ROW + 1:
            state["page"] = (state["page"] + 1) % MAX_PAGE
            selected_file %= MAX_PER_ROW


if exited_to_launcher or not woken_by_button:
    wait_for_user_to_release_buttons()
    display.set_update_speed(badger2350.UPDATE_MEDIUM)
    render()

display.set_update_speed(badger2350.UPDATE_TURBO)

#render()

while True:
    # Sometimes a button press or hold will keep the system
    # powered *through* HALT, so latch the power back on.
    #display.keepalive()


    if display.pressed(badger2350.BUTTON_A):
        button(badger2350.BUTTON_A)
    if display.pressed(badger2350.BUTTON_B):
        button(badger2350.BUTTON_B)
    if display.pressed(badger2350.BUTTON_C):
        button(badger2350.BUTTON_C)

    if display.pressed(badger2350.BUTTON_UP):
        button(badger2350.BUTTON_UP)
    if display.pressed(badger2350.BUTTON_DOWN):
        button(badger2350.BUTTON_DOWN)

    if changed:
        badger_os.state_save("launcher", state)
        changed = False
        render()

    display.halt()
