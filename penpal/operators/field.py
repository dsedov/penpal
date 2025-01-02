class ApplyField:
    def __init__(self, canvas, field):
        self.canvas = canvas
        self.field = field

    def apply(self, strength=1.0):
        for op in self.canvas.draw_stack:
            
            if op["type"] == "line":
                field_x, field_y = self.field.get_vector(op["x1"], op["y1"])
                op["x1"] += field_x * strength
                op["y1"] += field_y * strength
                field_x, field_y = self.field.get_vector(op["x2"], op["y2"])
                op["x2"] += field_x * strength
                op["y2"] += field_y * strength 

            if op["type"] == "point":
                field_x, field_y = self.field.get_vector(op["x"], op["y"])
                op["x"] += field_x * strength
                op["y"] += field_y * strength
