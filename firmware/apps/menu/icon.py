# icon colours
bold = color.black
faded = color.light_grey

# icon shape
shade_brush = color.dark_grey


class Icon:
    active_icon = None

    def __init__(self, pos, name, index, icon):
        self.active = False
        self.pos = pos
        self.icon = icon
        self.name = name
        self.index = index

    def activate(self, active):
        self.active = active
        if active:
            Icon.active_icon = self

    def draw(self):
        sprite_width = self.icon.width * 2
        sprite_offset = sprite_width / 2

        squircle = shape.rectangle(0, 0, 64, 64)

        # transform to the icon position
        x, y = self.pos
        squircle.transform = mat3().translate(x - 30, y - 30)
        screen.pen = bold
        screen.shape(squircle)

        squircle.transform = mat3().translate(x - 32, y - 32)
        screen.pen = faded
        screen.shape(squircle)

        if self.active:
            screen.pen = bold
            screen.shape(squircle.stroke(2))

        # draw the icon sprite
        if sprite_width > 0:
            self.icon.alpha = 255 if self.active else 100
            screen.blit(
                self.icon,
                rect(
                    self.pos[0] - sprite_offset,
                    self.pos[1] - 25,
                    sprite_width,
                    48
                )
            )
