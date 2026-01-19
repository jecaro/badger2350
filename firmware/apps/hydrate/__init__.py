import sys
import os
import math

sys.path.insert(0, "/system/apps/hydrate")
os.chdir("/system/apps/hydrate")

from badgeware import run, State, clamp

CX = screen.width / 2
CY = screen.height / 2

state = {
    "current": 0,
    "goal": 2000
}

background = brush.pattern(color.white, color.dark_grey, 12)

screen.antialias = image.X4

large_font = pixel_font.load("/system/assets/fonts/ignore.ppf")

graph_max = math.degrees(math.pi * 2)


def goal_met():
    return state["current"] >= state["goal"]


def draw_graph(x, y, r, value):

    screen.pen = color.white
    screen.shape(shape.circle(x, y, r + 10))

    v = clamp(value, 0, state["goal"])

    # scale the current amount in ml to degrees for our graph
    v = (v * (graph_max / state["goal"]))

    # rotate and position it so 0 is at the top
    pie = shape.pie(0, 0, r, 0, v)
    pie.transform = mat3().translate(x, y)

    screen.pen = color.dark_grey if not goal_met() else color.white
    screen.shape(shape.circle(x, y, r))

    screen.pen = color.white
    screen.shape(pie)
    screen.pen = color.white
    screen.shape(shape.circle(x, y, r - 8))

    screen.pen = color.dark_grey
    screen.shape(shape.circle(x, y, r - 8).stroke(2))
    screen.shape(shape.circle(x, y, r).stroke(2))

    # if the graph is big enough, put the text in the centre.
    if r > 30:
        screen.pen = color.black
        text = f"{state["current"]}ml"
        tw = screen.measure_text(text)[0]
        tx = x - tw / 2
        ty = y - 13
        screen.text(text, tx, ty)


MENU_OPEN_Y = CY
MENU_CLOSED_Y = screen.height - 15
menu_pos = [0, MENU_OPEN_Y, screen.width, screen.height - CY]
show_menu = False
menu_value = 0


def draw_menu():
    global menu_pos, show_menu, menu_value

    # unpack the menu position
    x, y, w, h = menu_pos

    # darken the background when the menu is showing
    if show_menu:

        mode(FAST_UPDATE)

        screen.pen = background
        screen.clear()

        # draw the menu background
        screen.pen = color.black
        screen.shape(shape.rounded_rectangle(x, y, w, h, 3, 3, 0, 0))

        # Show the menu elements if the menu is showing including during transition
        screen.pen = color.white
        t = f"{menu_value}ml"
        tx = CX - screen.measure_text(str(t))[0] / 2
        screen.text(t, tx, y + 52)
        screen.text("-", 43, y + 52)
        screen.text("+", 210, y + 52)
        screen.text("OK", screen.width - 28, y + 23)

        # gold star for meeting your daily goal! :)
        sx, sy = CX, y + 23
        if goal_met():
            screen.pen = color.white
            screen.shape(shape.star(sx, sy, 5, 9, 13))
        screen.pen = color.white
        screen.shape(shape.star(sx, sy, 5, 9, 13).stroke(2))
    else:
        screen.text("^", CX - 3, screen.height - 18)


def init():
    global state
    State.load("hydrate", state)


def update():
    global state, show_menu, menu_value

    mode(MEDIUM_UPDATE)

    screen.font = large_font

    if io.BUTTON_B in io.pressed:
        show_menu = not show_menu

    if show_menu:
        # increase/decrease the value to add
        # short press is +/- 5ml and long is +/- 25ml
        if io.BUTTON_A in io.pressed:
            menu_value -= 100
        if io.BUTTON_C in io.pressed:
            menu_value += 100

        if io.BUTTON_DOWN in io.pressed:
            state["current"] += menu_value
            menu_value = 0
            show_menu = not show_menu
            State.save("hydrate", state)

        if io.BUTTON_UP in io.held:
            state["current"] = 0
            State.save("hydrate", state)

        menu_value = clamp(menu_value, 0, state["goal"])

    screen.pen = background
    screen.clear()

    draw_graph(CX, CY - 8, 75, state["current"])
    draw_menu()


def on_exit():
    State.save("hydrate", state)


if __name__ == "__main__":
    run(update, init=init, on_exit=on_exit)
