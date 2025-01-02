class MinImpulseConstraint:
    def __init__(self, canvas, after_time=0.0, before_time=1000000000):
        self.canvas = canvas
        self.after_time = after_time
        self.before_time = before_time


    def apply(self, point, time_step):
        if time_step < self.after_time or time_step > self.before_time:
            return point
        if point["impulse"][0] < point["impulse"][1]:
            point["impulse"] = (point["impulse"][0] , 0.0)
        else:
            point["impulse"] = (0.0, point["impulse"][1])
        return point    
    
class MaxImpulseConstraint:
    def __init__(self, canvas, after_time=0.0, before_time=1000000000):
        self.canvas = canvas
        self.after_time = after_time
        self.before_time = before_time

    def apply(self, point, time_step):
        if time_step < self.after_time or time_step > self.before_time:
            return point
        if point["impulse"][0] > point["impulse"][1]:
            point["impulse"] = (point["impulse"][0] , 0.0)
        else:
            point["impulse"] = (0.0, point["impulse"][1])
        return point    