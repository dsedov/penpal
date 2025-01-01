from dataclasses import dataclass
from itertools import cycle
from typing import List, Tuple
import math

from penpal.simulation.attractor import Attractor

class SetMass:
    def __init__(self, canvas, mass=1.0):
        self.canvas = canvas
        self.mass = mass
        self.set()

    def set(self):
        for op in self.canvas.draw_stack:
            if op["type"] == "point":
                op["mass"] = self.mass

class SetImpulse:
    def __init__(self, canvas, impulse=1.0):
        self.canvas = canvas
        self.impulse = impulse
        self.set()

    def set(self):
        for op in self.canvas.draw_stack:
            if op["type"] == "point":
                op["impulse"] = self.impulse

class SetAsAttractor:
    def __init__(self, canvas, attractor=1.0):
        self.canvas = canvas
        self.attractor = attractor
        self.set()

    def set(self):
        for op in self.canvas.draw_stack:
            if op["type"] == "point":
                op["attractor"] = self.attractor

class Simulation:
    def __init__(self, canvas, forces=[]):
        self.canvas = canvas
        self.forces = forces

        # Physics constants
        self.G = 0.5  # Gravitational constant
        self.dt = 0.1  # Time step



    def simulate(self, steps=200):
        all_points = []
        all_attractor_points = []
        for point in self.canvas.draw_stack:
            if point["type"] == "point":
                all_points.append(point)
                if "attractor" in point and point["attractor"] > 0.01 and point["mass"] > 0.01:
                    all_attractor_points.append(point)

        for point in all_points:
            print(point)
            if "impulse" not in point:
                point["impulse"] = (0, 0)

            if "mass" not in point:
                point["mass"] = 1.0

            if "attractor" not in point:
                point["attractor"] = 0.0

            for _ in range(steps):    
                for force in self.forces:
                    force.apply(point)  

                for attractor_point in all_attractor_points:
                    attractor = Attractor.from_point(attractor_point)
                    attractor.apply(point)
                    
                start_x = point["x"]
                start_y = point["y"]


                point["x"] += point["impulse"][0] * self.dt
                point["y"] += point["impulse"][1] * self.dt

                end_x = point["x"]
                end_y = point["y"]
                self.canvas.line(start_x, start_y, end_x, end_y, color=point["color"], thickness=point["thickness"])
