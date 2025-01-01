import math
import numpy as np
class PointGrid:
    def __init__(self, canvas, 
                 vspacing=1.0, 
                 hspacing=1.0, 
                 additional_margin=0.0):
        self.canvas = canvas
        self.vspacing = vspacing
        self.hspacing = hspacing
        self.additional_margin = additional_margin

    def generate(self, density=1.0):
        for y in np.arange(self.canvas.margin + self.additional_margin, self.canvas.canvas_size_mm[1] - self.canvas.margin - self.additional_margin, self.vspacing):
            for x in np.arange(self.canvas.margin + self.additional_margin, self.canvas.canvas_size_mm[0] - self.canvas.margin - self.additional_margin, self.hspacing):
                self.canvas.point(x, y)

class ScatterPoints:
    def __init__(self, canvas):
        self.canvas = canvas

    def line_length(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def generate(self, density=1.0):

        for op in self.canvas.draw_stack:
            if op["type"] == "line":
                x1, y1 = op["x1"], op["y1"]
                x2, y2 = op["x2"], op["y2"]
                length = self.line_length(x1, y1, x2, y2)

                # Always add the start point
                self.canvas.point(x1, y1)

                if length > density:
                    # Calculate how many points we can fit
                    num_points = int(length / density)
                    
                    if num_points == 1:
                        # If we can only fit one point, put it in the middle
                        t = 0.5
                        x = x1 + t * (x2 - x1)
                        y = y1 + t * (y2 - y1)

                        self.canvas.point(x, y)
                    else:
                        # Distribute points evenly
                        for i in range(1, num_points):
                            t = i / num_points
                            x = x1 + t * (x2 - x1)
                            y = y1 + t * (y2 - y1)
                            self.canvas.point(x, y)

                # Add the end point
                self.canvas.point(x2, y2)
