import random

class ApplyNoise:
    def __init__(self, canvas, noise_x_level=0.5, noise_y_level=0.5):
        self.canvas = canvas
        self.noise_x_level = noise_x_level
        self.noise_y_level = noise_y_level

    def apply(self):
        prev_x_noise = 0
        prev_y_noise = 0
        for op in self.canvas.draw_stack:
            
            if op["type"] == "line":
                op["x1"] += prev_x_noise
                op["y1"] += prev_y_noise
                new_noise_x = random.uniform(-self.noise_x_level, self.noise_x_level)
                new_noise_y = random.uniform(-self.noise_y_level, self.noise_y_level)
                op["x2"] += new_noise_x
                op["y2"] += new_noise_y 
                prev_x_noise = new_noise_x
                prev_y_noise = new_noise_y
            
            if op["type"] == "point":
                op["x"] += prev_x_noise
                op["y"] += prev_y_noise
                prev_x_noise = new_noise_x
                prev_y_noise = new_noise_y

