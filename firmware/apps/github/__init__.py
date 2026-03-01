import os
import qrcode
import sys

sys.path.insert(0, "/system/apps/github")
os.chdir("/system/apps/github")


GITHUB_USERNAME = "jecaro"
DISPLAY_NAME = "JEAN-CHARLES"
OTHER = ""
CITY = "Dol-de-Bretagne"
COUNTRY = "France"


def measure_qr_code(size, qr):
    w, h = qr.get_size()
    module_size = int(size / w)
    return module_size * w, module_size


def draw_qr_code(ox, oy, size, qr):
    actual_size, module_size = measure_qr_code(size, qr)
    screen.pen = color.white
    screen.shape(shape.rectangle(ox, oy, actual_size, actual_size))
    screen.pen = color.black
    qr_w, qr_h = qr.get_size()
    for x in range(qr_w):
        for y in range(qr_h):
            if qr.get_module(x, y):
                screen.shape(
                    shape.rectangle(
                        ox + x * module_size,
                        oy + y * module_size,
                        module_size,
                        module_size,
                    )
                )
    return actual_size


def init():
    pass


def update():
    screen.antialias = screen.X2

    screen.pen = color.white
    screen.clear()

    # Border
    margin = 5
    screen.pen = color.black
    screen.shape(
        shape.rectangle(
            margin, margin, screen.width - margin * 2, screen.height - margin * 2
        ).stroke(3)
    )

    # Name and username
    screen.font = rom_font.ignore
    screen.text(DISPLAY_NAME, 95, 20)
    screen.text(f"@{GITHUB_USERNAME}", 95, 50)

    # Avatar
    avatar = image.load("avatar.png")
    screen.blit(avatar, vec2(15, 15))

    # Location and other info
    screen.font = rom_font.smart
    screen.text(CITY, 20, 100)
    screen.text(COUNTRY, 20, 120)
    screen.text(OTHER, 20, 140)

    # QR code
    code = qrcode.QRCode()
    code.set_text(f"https://github.com/{GITHUB_USERNAME}")
    draw_qr_code(195, 105, 70, code)

    badge.update()
    wait_for_button_or_alarm(timeout=5000)


def on_exit():
    pass


run(update)
