import random
class ApplyColor:
    def __init__(self, canvas, color, chance=0.5, field=None):
        self.canvas = canvas
        self.color = color
        self.chance = chance
        self.field = field

        self.apply(canvas)

    def apply(self, canvas):
        canvas.pen_color = self.color
        for draw_command in canvas.draw_stack:
            if self.field is None:
                if random.random() < self.chance:
                    draw_command["color"] = self.color
            else:
                if isinstance(self.color, list):
                    num_colors = len(self.color)
                    field_step = 1.0 / num_colors
                    if draw_command["type"] == "line":
                        color_index = int(self.field.get_float(draw_command["x1"], draw_command["y1"]) / field_step) - 1
                    else:
                        color_index = int(self.field.get_float(draw_command["x"], draw_command["y"]) / field_step) - 1
                    draw_command["color"] = self.color[color_index]
                else:
                    if self.field.get_value(draw_command["point"]) > 0.5:
                        draw_command["color"] = self.color
        return canvas
