import math

class PopulatePoints:
    def __init__(self, canvas):
        self.canvas = canvas
        self.points = []

    def line_length(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def generate(self, density=1.0):
        self.points = []  # Reset points list
        
        for op in self.canvas.draw_stack:
            if op["type"] == "line":
                x1, y1 = op["x1"], op["y1"]
                x2, y2 = op["x2"], op["y2"]
                length = self.line_length(x1, y1, x2, y2)

                # Always add the start point
                self.points.append((x1, y1))

                if length > density:
                    # Calculate how many points we can fit
                    num_points = int(length / density)
                    
                    if num_points == 1:
                        # If we can only fit one point, put it in the middle
                        t = 0.5
                        x = x1 + t * (x2 - x1)
                        y = y1 + t * (y2 - y1)
                        self.points.append((x, y))
                    else:
                        # Distribute points evenly
                        for i in range(1, num_points):
                            t = i / num_points
                            x = x1 + t * (x2 - x1)
                            y = y1 + t * (y2 - y1)
                            self.points.append((x, y))

                # Add the end point
                self.points.append((x2, y2))
                
        return self.points