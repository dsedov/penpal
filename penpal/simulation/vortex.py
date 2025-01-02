import math

class Vortex:
    def __init__(self, x, y, strength=1.0, after_time=0.0, before_time=1000000000):
        self.x = x
        self.y = y
        self.strength = strength
        self.after_time = after_time
        self.before_time = before_time

    def apply(self, point, time_step):     
        if time_step < self.after_time or time_step > self.before_time:
            return point
        # Vector from vortex center to point
        dx = point["x"] - self.x
        dy = point["y"] - self.y
        
        # Get angle between x-axis and vector to point
        angle = math.atan2(dy, dx)
        
        # Tangent vector components using trig
        # For clockwise rotation with positive strength:
        tx = -math.sin(angle)  # tangent x component
        ty = math.cos(angle)   # tangent y component
        
        point["impulse"] = (
            point["impulse"][0] + self.strength * tx,
            point["impulse"][1] + self.strength * ty
        )
        return point