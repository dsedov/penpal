import random
class ApplyColor:
    def __init__(self, canvas, color, chance=0.5):
        self.canvas = canvas
        self.color = color
        self.chance = chance

        self.apply(canvas)

    def apply(self, canvas):
        canvas.pen_color = self.color
        for draw_command in canvas.draw_stack:
            if random.random() < self.chance:
                draw_command["color"] = self.color
        return canvas
