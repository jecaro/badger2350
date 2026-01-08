# icon colours
bold = color.rgb(0, 0, 0 << 6)
faded = color.rgb(0, 0, 2 << 6)

# icon shape
shade_brush = color.rgb(0, 0, 1 << 6)


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
        width = 1
        sprite_width = self.icon.width * 2
        sprite_offset = sprite_width / 2

        squircle = shape.squircle(0, 0, 34, 4)

        # transform to the icon position
        squircle.transform = mat3().translate(*self.pos).scale(width, 1)

        screen.brush = faded

        screen.shape(squircle)

        if self.active:
            screen.brush = bold
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
