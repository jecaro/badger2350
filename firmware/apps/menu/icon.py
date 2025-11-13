from badgeware import brushes, shapes, Matrix, screen

# icon colours
bold = brushes.color(0, 0, 0 << 6)
faded = brushes.color(0, 0, 2 << 6)

# icon shape
shade_brush = brushes.color(0, 0, 1 << 6)


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

        squircle = shapes.squircle(0, 0, 34, 4)

        # transform to the icon position
        squircle.transform = Matrix().translate(*self.pos).scale(width, 1)

        screen.brush = faded

        screen.draw(squircle)

        if self.active:
            screen.brush = bold
            screen.draw(squircle.stroke(2))

        # draw the icon sprite
        if sprite_width > 0:
            self.icon.alpha = 255 if self.active else 100
            screen.scale_blit(
                self.icon,
                self.pos[0] - sprite_offset,
                self.pos[1] - 25,
                sprite_width,
                48,
            )
