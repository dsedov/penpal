class ApplyThickness:
    def __init__(self, thickness):
        self.thickness = thickness

    def apply(self, canvas):
        for draw_command in canvas.draw_stack:
            draw_command["thickness"] = self.thickness
        return canvas
