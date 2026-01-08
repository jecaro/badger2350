
import sys
import os

sys.path.insert(0, "/system/apps/menu")
os.chdir("/system/apps/menu")

import math
from badgeware import State, is_dir, file_exists, run
from icon import Icon
import ui

# define the list of installed apps
#
# - hack them!
# - replace them with your own
# - reorder them
# - what would mona do...?
apps = [
    ("mona's quest", "quest"),
    ("mona pet", "monapet"),
    ("monasketch", "sketch"),
    ("flappy mona", "flappy"),
    ("gallery", "gallery"),
    ("badge", "badge"),
]

mona = SpriteSheet("/system/assets/mona-sprites/mona-default.png", 11, 1)
screen.font = rom_font.ark
# screen.antialias = image.X2

# find installed apps and create icons
icons = []
for app in apps:
    name, path = app[0], app[1]

    if is_dir(f"/system/apps/{path}"):
        if file_exists(f"/system/apps/{path}/icon.png"):
            x = len(icons) % 3
            y = math.floor(len(icons) / 3)
            pos = (x * 88 + 43, y * 84 + 54)
            sprite = image.load(f"/system/apps/{path}/icon.png")
            icons.append(Icon(pos, name, len(icons), sprite))


state = {
    "active": 0,
    "running": "/system/apps/menu"
}
State.load("menu", state)


def update():
    global state, icons, alpha

    # process button inputs to switch between icons
    if io.BUTTON_C in io.pressed:
        state["active"] += 1
    if io.BUTTON_A in io.pressed:
        state["active"] -= 1
    if io.BUTTON_UP in io.pressed:
        state["active"] -= 3
    if io.BUTTON_DOWN in io.pressed:
        state["active"] += 3
    if io.BUTTON_B in io.pressed:
        state["running"] = f"/system/apps/{apps[state["active"]][1]}"
        State.modify("menu", state)
        return state["running"]
    
    if icons:
        state["active"] %= len(icons)

    State.modify("menu", state)

    ui.draw_background()
    ui.draw_header()

    # draw menu icons
    for i in range(len(icons)):
        icons[i].activate(state["active"] == i)
        icons[i].draw()

    # draw label for active menu icon
    if Icon.active_icon:
        label = f"{Icon.active_icon.name}"
        w, _ = screen.measure_text(label)
        screen.pen = color.rgb(0, 0, 0)
        screen.draw(shapes.rounded_rectangle((WIDTH / 2) - (w / 2) - 4, HEIGHT - 20, w + 8, 15, 4))
        screen.pen = color.rgb(255, 255, 255)
        screen.text(label, (WIDTH / 2) - (w / 2), HEIGHT - 19)

    return None


if __name__ == "__main__":
    run(update)
