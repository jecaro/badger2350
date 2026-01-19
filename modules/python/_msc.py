import rp2
from badgeware import run

rp2.enable_msc()

small_font = rom_font.winds
large_font = rom_font.nope


class DiskMode():
    def __init__(self):
        self.transferring = False

    def draw(self):
        screen.pen = brush.pattern(color.white, color.dark_grey, 23)
        screen.clear()

        # draw the main window
        window = (10, 10, screen.width - 20, screen.height - 20)
        offset = 2

        screen.pen = color.dark_grey
        screen.shape(shape.rectangle(window[0] + offset, window[1] + offset,
                                     window[2] + offset, window[3] + offset))
        screen.pen = color.white
        screen.shape(shape.rectangle(*window))
        screen.pen = color.black
        screen.shape(shape.rectangle(*window).stroke(2))

        screen.pen = color.black
        screen.shape(shape.rectangle(window[0], window[1], window[2], 30).stroke(1))

        # draw the accent lines in the title bar of the window
        x, y, w, h = window
        y += 6
        for i in range(5):
            y += 3
            screen.line(vec2(x, y), vec2(w + 10, y))

        screen.font = large_font
        title = "USB Disk Mode"
        tw, _ = screen.measure_text(title)

        title_pos = vec2((window[0] + window[2] // 2) - (tw // 2), window[1] + 9)
        screen.pen = color.white
        screen.rectangle(title_pos.x - 5, window[1] + 2, tw + 10, 26)
        screen.pen = color.black
        screen.text(title, title_pos.x, title_pos.y)

        screen.pen = color.dark_grey
        text_draw(screen, "1: Your badge is now mounted as a disk", rect(30, 45, 210, 100))
        text_draw(screen, "2: Copy code onto it to experiment!", rect(30, 85, 210, 100))
        text_draw(screen, "3: Eject the disk to reboot your badge", rect(30, 125, 210, 100))


def center_text(text, y):
    w, h = screen.measure_text(text)
    screen.text(text, 80 - (w / 2), y)


disk_mode = DiskMode()


def update():
    # set transfer state here
    disk_mode.transferring = rp2.is_msc_busy()

    # draw the ui
    disk_mode.draw()


run(update)
