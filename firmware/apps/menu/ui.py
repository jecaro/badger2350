from badgeware import get_battery_level, is_charging

black = color.rgb(0, 0, 0 << 6)
background = color.rgb(0, 0, 3 << 6)
gray = color.rgb(0, 0, 2 << 6)


def draw_background():
    # draw over the corners in black ready for the rounded rectangle that makes
    # up most of the background
    screen.pen = color.rgb(255, 255, 255)
    screen.clear()

    # draw the faux crt shape background area
    screen.pen = background
    screen.shape(shape.rounded_rectangle(0, 0, screen.width, screen.height, 8))


def draw_header():
    # create animated header text
    label = "Mona-OS v4.03"
    pos = (5, 2)

    screen.pen = black
    screen.shape(shape.rounded_rectangle(0, 0, screen.width, 15, 8, 8, 0, 0))

    screen.pen = background
    screen.text(label, *pos)

    # draw the battery indicator
    if is_charging():
        battery_level = (io.ticks / 20) % 100
    else:
        battery_level = get_battery_level()
    pos = (screen.width - 30, 4)
    size = (16, 8)
    screen.pen = background
    screen.shape(shape.rectangle(*pos, *size))
    screen.shape(shape.rectangle(pos[0] + size[0], pos[1] + 2, 1, 4))
    screen.pen = black
    screen.shape(shape.rectangle(pos[0] + 1, pos[1] + 1, size[0] - 2, size[1] - 2))

    # draw the battery fill level
    width = ((size[0] - 4) / 100) * battery_level
    screen.pen = background
    screen.shape(shape.rectangle(pos[0] + 2, pos[1] + 2, width, size[1] - 4))
