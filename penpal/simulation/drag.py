class Drag:
    def __init__(self, canvas, drag=0.5, after_time=0.0, before_time=1000000000):
        self.canvas = canvas
        self.drag = drag
        self.after_time = after_time
        self.before_time = before_time

    def apply(self, point, time_step):
        if time_step < self.after_time or time_step > self.before_time:
            return point
        point["impulse"] = (point["impulse"][0] * (1.0 - self.drag), point["impulse"][1] * (1.0 - self.drag))
        return point    