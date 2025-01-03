class Drag:
    def __init__(self, canvas, drag=0.5, field=None, after_time=0.0, before_time=1000000000):
        self.canvas = canvas
        self.drag = drag
        self.field = field
        self.after_time = after_time
        self.before_time = before_time

    def apply(self, point, time_step, all_points = []):
        if time_step < self.after_time or time_step > self.before_time:
            return point
        if self.field is not None:  
            drag = self.field.get_float(point["x"], point["y"]) * self.drag
        else:
            drag = self.drag

        drag = max(drag, 0.0)
        drag = min(drag, 1.0)
        point["impulse"] = (point["impulse"][0] * (1.0 - drag), point["impulse"][1] * (1.0 - drag))
        return point    
    
class BorderDrag:
    def __init__(self, canvas, drag=0.5, field=None, after_time=0.0, before_time=1000000000):
        self.canvas = canvas
        self.drag = drag
        self.field = field
        self.after_time = after_time
        self.before_time = before_time

    def apply(self, point, time_step, all_points = []):
        if time_step < self.after_time or time_step > self.before_time:
            return point
        if point["x"] > self.canvas.top_left[0] and point["x"] < self.canvas.bottom_right[0] and point["y"] > self.canvas.top_left[1] and point["y"] < self.canvas.bottom_right[1]:
            return point
        
        if self.field is not None:  
            drag = self.field.get_float(point["x"], point["y"]) * self.drag
        else:
            drag = self.drag
        
        drag = max(drag, 0.0)
        drag = min(drag, 1.0)

        point["impulse"] = (point["impulse"][0] * (1.0 - drag), point["impulse"][1] * (1.0 - drag))
        return point    


