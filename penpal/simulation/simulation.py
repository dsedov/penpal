from dataclasses import dataclass
from itertools import cycle
from typing import List, Tuple
import random
import math
import tqdm

from penpal.simulation.attractor import Attractor

class SetMass:
    def __init__(self, canvas, mass=1.0, chance=1.0):
        self.canvas = canvas
        self.mass = mass
        self.chance = chance
        self.set()

    def set(self):
        for op in self.canvas.draw_stack:
            if op["type"] == "point":
                if random.random() < self.chance:
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
    def __init__(self, canvas, attractor=1.0, chance=1.0):
        self.canvas = canvas
        self.attractor = attractor
        self.chance = chance
        self.set()

    def set(self):
        for op in self.canvas.draw_stack:
            if op["type"] == "point":
                if random.random() < self.chance:
                    op["attractor"] = self.attractor

class Simulation:
    def __init__(self, canvas, forces=[], events=[], dt = 0.1, start_lines_at=0, type="sequential", 
                 collision_detection=False, 
                 collision_type="line", 
                 collision_damping=0.1,
                 collision_flip_mass=False):
        self.canvas = canvas
        self.forces = forces
        self.events = events
        self.type = type
        self.collision_detection = collision_detection
        self.collision_type = collision_type
        self.collision_damping = collision_damping

        # Physics constants
        self.G = 0.5  # Gravitational constant
        self.dt = dt  # Time step
        self.start_lines_at = start_lines_at

        # Add grid parameters
        self.cell_size = 10  # Adjust based on your typical line lengths
        self.grid = {}  # Dictionary of (cell_x, cell_y) -> list of line segments
        self.collision_buffer_steps = 5
        self.collision_flip_mass = collision_flip_mass

    def simulate(self, steps=200):
        all_points = []
        all_attractor_points = []
        for point in self.canvas.draw_stack:
            if point["type"] == "point":
                all_points.append(point)
                if "attractor" in point and point["attractor"] > 0.01 and point["mass"] > 0.01:
                    all_attractor_points.append(point)

        if self.type == "sequential":
            for point in tqdm.tqdm(all_points):
    
                if "impulse" not in point:
                    point["impulse"] = (0, 0)

                if "mass" not in point:
                    point["mass"] = 1.0

                if "attractor" not in point:
                    point["attractor"] = 0.0

                for time_step in range(steps):    
                    for force in self.forces:
                        force.apply(point, time_step)  

                    for attractor_point in all_attractor_points:
                        if attractor_point == point:
                            continue
                        attractor = Attractor.from_point(attractor_point)
                        attractor.apply(point, time_step)
                        
                    start_x = point["x"]
                    start_y = point["y"]


                    point["x"] += point["impulse"][0] * self.dt
                    point["y"] += point["impulse"][1] * self.dt

                    end_x = point["x"]
                    end_y = point["y"]
                    self.canvas.line(start_x, start_y, end_x, end_y, color=point["color"], thickness=point["thickness"])

        elif self.type == "concurrent":
            for time_step in tqdm.tqdm(range(steps)):
                for point in all_points:
    
                    if "impulse" not in point:
                        point["impulse"] = (0, 0)

                    if "mass" not in point:
                        point["mass"] = 1.0

                    if "attractor" not in point:
                        point["attractor"] = 0.0

      
                    for force in self.forces:
                        force.apply(point, time_step)  

                    for attractor_point in all_attractor_points:
                        if attractor_point == point:
                            continue
                        attractor = Attractor.from_point(attractor_point)
                        attractor.apply(point, time_step)
                        
                    start_x = point["x"]
                    start_y = point["y"]


                    
                    if self.collision_detection:    
                        if self._check_collision(point["x"], point["y"], point["x"] + point["impulse"][0] * self.dt, point["y"] + point["impulse"][1] * self.dt, time_step):
                            # Handle collision (e.g., reflect impulse)
                            point["impulse"] = (-point["impulse"][0] * (1.0-self.collision_damping), -point["impulse"][1] * (1.0-self.collision_damping))

                    point["x"] += point["impulse"][0] * self.dt
                    point["y"] += point["impulse"][1] * self.dt

                    end_x = point["x"]
                    end_y = point["y"]    
                    if time_step >= self.start_lines_at:
                        self.canvas.line(start_x, start_y, end_x, end_y, color=point["color"], thickness=point["thickness"])
                        if self.collision_flip_mass:
                            point["mass"] = -point["mass"]
                        self._add_line_to_grid(start_x, start_y, end_x, end_y, time_step)


    def _get_cells_for_line(self, x1, y1, x2, y2):
        """Get all grid cells that a line segment passes through"""
        # Convert to grid coordinates
        start_cell = (int(x1 / self.cell_size), int(y1 / self.cell_size))
        end_cell = (int(x2 / self.cell_size), int(y2 / self.cell_size))
        
        cells = set()
        dx = abs(end_cell[0] - start_cell[0])
        dy = abs(end_cell[1] - start_cell[1])
        
        # Handle straight lines
        if dx == 0:  # Vertical line
            y_start = min(start_cell[1], end_cell[1])
            y_end = max(start_cell[1], end_cell[1])
            return {(start_cell[0], y) for y in range(y_start, y_end + 1)}
            
        if dy == 0:  # Horizontal line
            x_start = min(start_cell[0], end_cell[0])
            x_end = max(start_cell[0], end_cell[0])
            return {(x, start_cell[1]) for x in range(x_start, x_end + 1)}
        
        # Handle diagonal and other lines
        if dx > dy:
            step = 1 if end_cell[0] > start_cell[0] else -1
            slope = dy / dx  # Won't divide by zero since dx > dy > 0
            for x in range(start_cell[0], end_cell[0] + step, step):
                y = int(start_cell[1] + slope * (x - start_cell[0]))
                cells.add((x, y))
        else:
            step = 1 if end_cell[1] > start_cell[1] else -1
            slope = dx / dy  # Won't divide by zero since dy >= dx > 0
            for y in range(start_cell[1], end_cell[1] + step, step):
                x = int(start_cell[0] + slope * (y - start_cell[1]))
                cells.add((x, y))
                
        return cells
    
    def _line_segment_intersection(self, x1, y1, x2, y2, x3, y3, x4, y4):
        """Check if two line segments intersect"""
        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denominator == 0:
            return False
            
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator
        
        return 0 <= t <= 1 and 0 <= u <= 1
        
    def _add_line_to_grid(self, x1, y1, x2, y2, time_step):
        """Add a line segment to the spatial grid"""
        cells = self._get_cells_for_line(x1, y1, x2, y2)
        # Store the timestep along with the line coordinates
        line_segment = (x1, y1, x2, y2, time_step)
        
        for cell in cells:
            if cell not in self.grid:
                self.grid[cell] = []
            self.grid[cell].append(line_segment)
            
    def _check_collision(self, x1, y1, x2, y2, current_time_step):
        """Check if a new line segment would collide with existing lines"""
        cells = self._get_cells_for_line(x1, y1, x2, y2)
        
        for cell in cells:
            if cell in self.grid:
                for line in self.grid[cell]:
                    # Unpack the line data including its timestep
                    x3, y3, x4, y4, line_time_step = line
                    
                    # Only check collision if the line is old enough
                    if current_time_step - line_time_step > self.collision_buffer_steps:
                        if self._line_segment_intersection(x1, y1, x2, y2, x3, y3, x4, y4):
                            return True
        return False