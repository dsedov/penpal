import math

class SubdivideLines:
    def __init__(self, canvas, min_length=1.0):
        self.canvas = canvas
        self.min_length = min_length

    def line_length(self, op):
        return math.sqrt((op["x2"] - op["x1"])**2 + (op["y2"] - op["y1"])**2)

    def apply(self):
        new_stack = []
        for op in self.canvas.draw_stack:
            if op["type"] == "line":
                length = self.line_length(op)
                if length < self.min_length:
                    new_stack.append(op)  # Keep short lines as-is
                    continue

                # Subdivide the line into smaller lines
                x1, y1 = op["x1"], op["y1"]
                x2, y2 = op["x2"], op["y2"]
                num_segments = max(2, int(length / self.min_length))
                
                # Create continuous segments
                for i in range(num_segments):
                    t1 = i / num_segments
                    t2 = (i + 1) / num_segments
                    
                    # Start point of segment
                    x_start = x1 + t1 * (x2 - x1)
                    y_start = y1 + t1 * (y2 - y1)
                    
                    # End point of segment
                    x_end = x1 + t2 * (x2 - x1)
                    y_end = y1 + t2 * (y2 - y1)
                    
                    new_stack.append({
                        "type": "line",
                        "x1": x_start,
                        "y1": y_start,
                        "x2": x_end,
                        "y2": y_end,
                        "color": op["color"],
                        "thickness": op["thickness"]
                    })
            else:
                new_stack.append(op)  # Keep non-line operations as-is
                
        self.canvas.draw_stack = new_stack

