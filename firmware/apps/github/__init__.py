import os
import qrcode
import sys

sys.path.insert(0, "/system/apps/github")
os.chdir("/system/apps/github")

page = 0
nb_pages = 2


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
    global page, nb_pages

    if badge.pressed(BUTTON_UP):
        page = (page + 1) % nb_pages
    if badge.pressed(BUTTON_DOWN):
        page = (page - 1) % nb_pages

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

    # First page with avatar and info
    if page == 0:
        # Avatar
        avatar = image.load("avatar.png")
        screen.blit(avatar, vec2(15, 15))

        # Name and username
        screen.font = rom_font.ignore
        screen.text("Jean-Charles", 95, 20)
        screen.text("@jecaro", 95, 50)

        # Location and other info
        screen.font = rom_font.smart
        screen.text("Dol-de-Bretagne, France", 20, 101)

        haskell = image.load("haskell.png")
        haskell.onebit()
        screen.blit(haskell, vec2(20, 124))

        rust = image.load("rust.png")
        rust.onebit()
        screen.blit(rust, vec2(67, 124))

        nixos = image.load("nixos.png")
        nixos.onebit()
        screen.blit(nixos, vec2(110, 124))

        # QR code
        code = qrcode.QRCode(qrcode.ECC_LOW)
        code.set_text("https://github.com/jecaro")
        draw_qr_code(195, 105, 70, code)

    # Second page with contact info
    elif page == 1:
        screen.font = rom_font.smart
        offset_x = 25
        offset_y = 20
        y_step = 20

        screen.text("jeancharles.quillet@gmail.com", offset_x, offset_y)
        offset_y += y_step

        screen.text("https://jeancharles.quillet.org", offset_x, offset_y)
        offset_y += y_step

        screen.text("https://github.com/jecaro", offset_x, offset_y)

        code = qrcode.QRCode(qrcode.ECC_LOW)
        code.set_text("jeancharles.quillet@gmail.com")
        draw_qr_code(25, 95, 70, code)

        code = qrcode.QRCode(qrcode.ECC_LOW)
        code.set_text("https://jeancharles.quillet.org")
        draw_qr_code(106, 95, 70, code)

        code = qrcode.QRCode(qrcode.ECC_LOW)
        code.set_text("https://github.com/jecaro")
        draw_qr_code(183, 95, 70, code)

    badge.update()
    wait_for_button_or_alarm(timeout=5000)


def on_exit():
    pass


run(update)
