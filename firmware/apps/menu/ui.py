from badgeware import brushes, shapes, io, screen, get_battery_level, is_charging, WIDTH, HEIGHT

black = brushes.color(0, 0, 0 << 6)
background = brushes.color(0, 0, 3 << 6)
gray = brushes.color(0, 0, 2 << 6)


def draw_background():
    # draw over the corners in black ready for the rounded rectangle that makes
    # up most of the background
    screen.brush = brushes.color(255, 255, 255)
    screen.clear()

    # draw the faux crt shape background area
    screen.brush = background
    screen.draw(shapes.rounded_rectangle(0, 0, WIDTH, HEIGHT, 8))


def draw_header():
    # create animated header text
    label = "Mona-OS v4.03"
    pos = (5, 2)

    screen.brush = black
    screen.draw(shapes.rounded_rectangle(0, 0, WIDTH, 15, 8, 8, 0, 0))

    screen.brush = background
    screen.text(label, *pos)

    # draw the battery indicator
    if is_charging():
        battery_level = (io.ticks / 20) % 100
    else:
        battery_level = get_battery_level()
    pos = (WIDTH - 30, 4)
    size = (16, 8)
    screen.brush = background
    screen.draw(shapes.rectangle(*pos, *size))
    screen.draw(shapes.rectangle(pos[0] + size[0], pos[1] + 2, 1, 4))
    screen.brush = black
    screen.draw(shapes.rectangle(pos[0] + 1, pos[1] + 1, size[0] - 2, size[1] - 2))

    # draw the battery fill level
    width = ((size[0] - 4) / 100) * battery_level
    screen.brush = background
    screen.draw(shapes.rectangle(pos[0] + 2, pos[1] + 2, width, size[1] - 4))
