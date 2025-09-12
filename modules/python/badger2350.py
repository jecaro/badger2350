import machine
import powman
from picographics import PicoGraphics, DISPLAY_BADGER_2350

# We can rely on these having been set up by powman... maybe
BUTTON_DOWN = machine.Pin.board.BUTTON_DOWN
BUTTON_A = machine.Pin.board.BUTTON_A
BUTTON_B = machine.Pin.board.BUTTON_B
BUTTON_C = machine.Pin.board.BUTTON_C
BUTTON_UP = machine.Pin.board.BUTTON_UP
BUTTON_HOME = machine.Pin.board.BUTTON_HOME

UPDATE_NORMAL = 0
UPDATE_MEDIUM = 1
UPDATE_FAST = 2
UPDATE_TURBO = 3

WIDTH = 264
HEIGHT = 176

SYSTEM_FREQS = [
    4000000,
    12000000,
    48000000,
    133000000,
    250000000
]

BUTTONS = (
    BUTTON_DOWN,
    BUTTON_A,
    BUTTON_B,
    BUTTON_C,
    BUTTON_UP,
    BUTTON_HOME
)


def is_wireless():
    return True


def woken_by_button():
    return powman.get_wake_reason() in (
        powman.WAKE_BUTTON_A,
        powman.WAKE_BUTTON_B,
        powman.WAKE_BUTTON_C,
        powman.WAKE_BUTTON_UP,
        powman.WAKE_BUTTON_DOWN)


def pressed_to_wake(button):
    # TODO: BUTTON_HOME cannot be a wake button
    # so maybe raise an exception
    return button in powman.get_wake_buttons()


def woken_by_reset():
    return powman.get_wake_reason() == 255


def system_speed(speed):
    try:
        machine.freq(SYSTEM_FREQS[speed])
    except IndexError:
        pass


class Badger2350():
    def __init__(self):
        self.display = PicoGraphics(DISPLAY_BADGER_2350)
        self._update_speed = 0

    def __getattr__(self, item):
        # Glue to redirect calls to PicoGraphics
        return getattr(self.display, item)

    def update(self):
        t_start = time.ticks_ms()
        self.display.update()
        t_elapsed = time.ticks_ms() - t_start

        delay_ms = [4700, 2600, 900, 250][self._update_speed]

        if t_elapsed < delay_ms:
            time.sleep((delay_ms - t_elapsed) / 1000)

    def set_update_speed(self, speed):
        self.display.set_update_speed(speed)
        self._update_speed = speed


    def pressed(self, button):
        return button.value() == 0

    def pressed_any(self):
        return 0 in [button.value() for button in BUTTONS]

    def sleep(self):
        powman.sleep()
