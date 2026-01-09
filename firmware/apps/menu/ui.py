from badgeware import get_battery_level, is_charging

black = color.rgb(0, 0, 0 << 6)
background = color.rgb(0, 0, 3 << 6)
gray = color.rgb(0, 0, 2 << 6)
white = color.rgb(0, 0, 3 << 6)


def draw_background():
    # draw over the corners in black ready for the rounded rectangle that makes
    # up most of the background
    screen.pen = black
    screen.clear()

    # draw the faux crt shape background area
    screen.pen = brush.pattern(white, gray, 23)
    screen.shape(shape.rectangle(0, 0, screen.width, screen.height))


def draw_header():
    # create animated header text
    label = "BadgerOS v4.03"
    w, _ = screen.measure_text(label)
    pos = ((screen.width / 2) - (w / 2), 1)

    screen.pen = white
    screen.shape(shape.rectangle(0, 0, screen.width, 15))

    screen.pen = black
    screen.line(4, 4, screen.width - 4, 4)
    screen.line(4, 6, screen.width - 4, 6)
    screen.line(4, 8, screen.width - 4, 8)
    screen.line(4, 10, screen.width - 4, 10)
    screen.line(0, 15, screen.width, 15)

    screen.pen = white
    screen.shape(shape.rectangle(pos[0] - 5, 0, w + 10, 15))

    screen.pen = black
    screen.text(label, *pos)

    # draw the battery indicator
    if is_charging():
        battery_level = (io.ticks / 20) % 100
    else:
        battery_level = get_battery_level()
    pos = (screen.width - 30, 4)
    size = (16, 8)
    screen.pen = white
    screen.shape(shape.rectangle(pos[0] - 3, 0, size[0] + 7, 15))
    screen.pen = black
    screen.shape(shape.rectangle(*pos, *size))
    screen.shape(shape.rectangle(pos[0] + size[0], pos[1] + 2, 1, 4))
    screen.pen = white
    screen.shape(shape.rectangle(pos[0] + 1, pos[1] + 1, size[0] - 2, size[1] - 2))

    # draw the battery fill level
    width = ((size[0] - 4) / 100) * battery_level
    screen.pen = black
    screen.shape(shape.rectangle(pos[0] + 2, pos[1] + 2, width, size[1] - 4))
