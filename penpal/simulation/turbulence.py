import random

class Turbulence:
    def __init__(self, canvas, turbulence=0.1, after_time=0.0, before_time=1000000000):
        self.canvas = canvas
        self.turbulence = turbulence
        self.after_time = after_time
        self.before_time = before_time

    def apply(self, point, time_step):
        if time_step < self.after_time or time_step > self.before_time:
            return point
        point["impulse"] = ( 
            point["impulse"][0] + random.uniform(-self.turbulence, self.turbulence), 
            point["impulse"][1] + random.uniform(-self.turbulence, self.turbulence)
            )
        return point