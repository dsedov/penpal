class Collision:
    def __init__(self, canvas):
        self.canvas = canvas

    def apply(self, point, radius=0.5):
        if point["impulse"][0] < 0.0001 and point["impulse"][1] < 0.0001:
            return
        if self.canvas.check_collision(point["x"] + point["impulse"][0]*radius, point["y"] + point["impulse"][1]*radius, radius):
            point["impulse"] = (0, 0)
