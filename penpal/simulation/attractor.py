import math

class Attractor:
    def __init__(self, attractor=(0.0, 0.0), strength=0.5):
        self.attractor = attractor
        self.strength = strength
        self.mass = 1.0

    def from_point(point):
        attractor = Attractor()
        attractor.attractor = (point["x"], point["y"])
        attractor.strength = point["attractor"]
        attractor.mass = point["mass"]
        return attractor

    def apply(self, point):
        distance = math.sqrt((self.attractor[0] - point["x"])**2 + (self.attractor[1] - point["y"])**2) 
        distance = max(distance, 1.0)
        force = (point["mass"] * self.strength) / (distance * distance)
        point["impulse"] = (
            point["impulse"][0] + force * (self.attractor[0] - point["x"]) / distance, 
            point["impulse"][1] + force * (self.attractor[1] - point["y"]) / distance
        )
        return point