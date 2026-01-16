from badgeware import run
import rp2

rp2.enable_msc()


try:
    small_font = rom_font.ark
    large_font = rom_font.absolute
except OSError:
    small_font = None
    large_font = None


class DiskMode():
    def __init__(self):
        self.transferring = False

    def draw(self):
        screen.pen = color.white
        screen.clear()

        if large_font:
            screen.font = large_font
            screen.pen = color.dark_grey
            center_text("USB Disk Mode", 5)

            screen.text("1:", 10, 25)
            screen.text("2:", 10, 45)
            screen.text("3:", 10, 65)

            screen.pen = color.dark_grey
            screen.font = small_font
            wrap_text("""Your badge is now mounted as a disk""", 30, 28)

            wrap_text("""Copy code onto it to experiment!""", 30, 48)

            wrap_text("""Eject the disk to reboot your badge""", 30, 68)

            screen.font = small_font
            if self.transferring:
                screen.pen = color.dark_grey
                center_text("Transferring data!", 102)
            else:
                screen.pen = color.light_grey
                center_text("Waiting for data", 102)


def center_text(text, y):
    w, h = screen.measure_text(text)
    screen.text(text, 80 - (w / 2), y)


def wrap_text(text, x, y):
    lines = text.splitlines()
    for line in lines:
        _, h = screen.measure_text(line)
        screen.text(line, x, y)
        y += h * 0.8


disk_mode = DiskMode()


def update():
    # set transfer state here
    disk_mode.transferring = rp2.is_msc_busy()

    # draw the ui
    disk_mode.draw()


run(update)
