import numpy as np
class Canvas:
    def __init__(self, canvas_size_mm = (356.0, 432.0), paper_color="white", pen_color="black"):
        self.canvas_size_mm = canvas_size_mm
        self.paper_color = paper_color
        self.pen_color = pen_color
        self.draw_stack = []

    def line(self, x1, y1, x2, y2, color=None, thickness=1.0):
        self.draw_stack.append({
            "type": "line",
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "color": color,
            "thickness": thickness
        })
    
    def box(self, x, y, w, h, color=None, thickness=1.0, filled=False):
        self.line(x, y, x + w, y, color, thickness)
        self.line(x + w, y, x + w, y + h, color, thickness)
        self.line(x + w, y + h, x, y + h, color, thickness)
        self.line(x, y + h, x, y, color, thickness)
        if filled:
            step = thickness
            
            for i in np.arange(step, h, step):
                self.line(x, y + i, x + w, y + i, color, thickness)
