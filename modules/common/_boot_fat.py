import os
import rp2
import vfs
import machine  # noqa: F401
import powman


# Try to mount the filesystem, and format the flash if it doesn't exist.
bdev = rp2.Flash()
try:
    fat = vfs.VfsFat(bdev)
    fat.label("Badger2350")
    vfs.mount(fat, "/")
    os.listdir("/") # might fail with UnicodeError on corrupt FAT

except:  # noqa: E722
    vfs.VfsFat.mkfs(bdev)
    fat = vfs.VfsFat(bdev)
    fat.label("Badger2350")
    vfs.mount(fat, "/")


if powman.get_wake_reason() == powman.WAKE_DOUBLETAP:
    from picographics import PicoGraphics, DISPLAY_BADGER_2350
    self.display = PicoGraphics(DISPLAY_BADGER_2350)
    display.set_pen(0)
    display.clear()
    display.set_pen(0x22)
    display.text("USB\nDisk\nMode", 1, 0, scale=4)
    display.update()
    rp2.enable_msc()

del os, vfs, bdev
