import random

class Split:
    def __init__(self, canvas, on=["collision"], chance=1.0):
        self.canvas = canvas
        self.chance = chance
        self.on = on

    def apply(self, point, time_step):
        if random.random() < self.chance:
            new_point = point.copy()
            new_point["impulse"] = (-point["impulse"][0], -point["impulse"][1])
            self.canvas.draw_stack.append(new_point)


class FlipMass:
    def __init__(self, canvas, on=["near"], chance=1.0):
        self.canvas = canvas
        self.chance = chance
        self.on = on

    def apply(self, point, time_step):
        if random.random() < self.chance:
            point["mass"] = -point["mass"]

