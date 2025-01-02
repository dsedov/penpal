class Drag:
    def __init__(self, canvas, drag=0.5):
        self.canvas = canvas
        self.drag = drag

    def apply(self, point):
        point["impulse"] = (point["impulse"][0] * (1.0 - self.drag), point["impulse"][1] * (1.0 - self.drag))
        return point    