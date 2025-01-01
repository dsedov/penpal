import random

class Turbulence:
    def __init__(self, canvas, turbulence=0.1):
        self.canvas = canvas
        self.turbulence = turbulence

    def apply(self, point):
        point["impulse"] = ( 
            point["impulse"][0] + random.uniform(-self.turbulence, self.turbulence), 
            point["impulse"][1] + random.uniform(-self.turbulence, self.turbulence)
            )
        return point