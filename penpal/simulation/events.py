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
    def __init__(self, canvas, on=["near_point"], chance=1.0, distance=10.0, max_time_between_flips=10):
        self.canvas = canvas
        self.chance = chance
        self.on = on
        self.distance = distance
        self.last_flip = 0.0
        self.max_time_between_flips = max_time_between_flips

    def apply(self, point, time_step, with_point=None):
        if time_step - self.last_flip > self.max_time_between_flips:
            if random.random() < self.chance:
                point["mass"] = -point["mass"]
                point["impulse"] = (-point["impulse"][0], -point["impulse"][1])
                self.last_flip = time_step


