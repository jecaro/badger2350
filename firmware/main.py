# This file is copied from /system/main.py to /main.py on first run

import sys
import os
from badgeware import run, State
import machine


def quit_to_launcher(pin):
    global running_app, state

    state["running"] = "/system/apps/menu"
    State.modify("menu", state)

    getattr(running_app, "on_exit", lambda: None)()
    # If we reset while boot is low, bad times
    while not pin.value():
        pass
    machine.reset()


state = {
    "active": 0,
    "running": "/system/apps/menu"
}
State.load("menu", state)

running_app = state["running"]

machine.Pin.board.BUTTON_HOME.irq(
    trigger=machine.Pin.IRQ_FALLING, handler=quit_to_launcher
)


app = running_app

sys.path.insert(0, app)
os.chdir(app)

running_app = __import__(app)

getattr(running_app, "init", lambda: None)()

run(running_app.update)

# Unreachable, in theory!
machine.reset()
