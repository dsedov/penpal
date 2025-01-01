class ApplyField:
    def __init__(self, canvas, field):
        self.canvas = canvas
        self.field = field

    def apply(self, strength=1.0):
        prev_x_field = 0
        prev_y_field = 0
        for op in self.canvas.draw_stack:
            
            if op["type"] == "line":
                op["x1"] += prev_x_field
                op["y1"] += prev_y_field
                new_field_x, new_field_y = self.field.get_vector(op["x1"], op["y1"])
                op["x2"] += new_field_x * strength
                op["y2"] += new_field_y * strength 
                prev_x_field = new_field_x * strength
                prev_y_field = new_field_y * strength

            if op["type"] == "point":
                op["x"] += prev_x_field
                op["y"] += prev_y_field
                prev_x_field = new_field_x * strength
                prev_y_field = new_field_y * strength
