from dataclasses import dataclass
from itertools import cycle
from typing import List, Tuple
import random
import math
import tqdm

from penpal.simulation.attractor import Attractor

class SetMass:
    def __init__(self, canvas, mass=1.0, chance=1.0, mode="set", field=None):
        self.canvas = canvas
        self.mass = mass
        self.chance = chance
        self.field = field
        self.mode = mode
        self.set()

    def set(self):
        for op in self.canvas.draw_stack:
            if op["type"] == "point":
                if random.random() < self.chance:
                    if self.field is not None:
                        if self.mode == "set":
                            op["mass"] = self.field.get_float(op["x"], op["y"]) * self.mass
                        elif self.mode == "add":
                            op["mass"] += self.field.get_float(op["x"], op["y"])
                    else:
                        if self.mode == "set":
                            op["mass"] = self.mass
                        elif self.mode == "add":
                            op["mass"] += self.mass


class SetImpulse:
    def __init__(self, canvas, impulse=1.0, chance=1.0, mode="set", field=None, randomize=False):
        self.canvas = canvas
        self.impulse = impulse
        self.chance = chance
        self.field = field
        self.mode = mode
        self.randomize = randomize
        self.set()

    def set(self):
        for op in self.canvas.draw_stack:
            if op["type"] == "point":
                if random.random() < self.chance:
                    if self.field is not None:
                        if self.mode == "set":
                            op["impulse"] = (self.field.get_float(op["x"], op["y"]) * self.impulse[0], self.field.get_float(op["x"], op["y"]) * self.impulse[1])
                        elif self.mode == "add":
                            op["impulse"] = (op["impulse"][0] + self.field.get_float(op["x"], op["y"]) * self.impulse[0], op["impulse"][1] + self.field.get_float(op["x"], op["y"]) * self.impulse[1])
                    else:
                        if self.mode == "set":
                            if self.randomize:
                                op["impulse"] = (random.uniform(-self.impulse[0], self.impulse[0]), random.uniform(-self.impulse[1], self.impulse[1]))
                            else:
                                op["impulse"] = self.impulse
                        elif self.mode == "add":
                            if self.randomize:
                                op["impulse"] = (op["impulse"][0] + random.uniform(-self.impulse[0], self.impulse[0]), op["impulse"][1] + random.uniform(-self.impulse[1], self.impulse[1]))
                            else:
                                op["impulse"] = (op["impulse"][0] + self.impulse[0], op["impulse"][1] + self.impulse[1])
    
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
                    if self.attractor > 0.01:
                        op["live"] = True

class Simulation:
    def __init__(self, canvas, forces=[], events=[], on_step_end=[], dt=0.1, start_lines_at=0, type="sequential",
                 collision_detection=False,
                 collision_type="line",
                 collision_damping=0.1,
                 collision_flip_mass=False,
                 repel=False,
                 repel_force=1.0,
                 repel_radius=10.0):
        self.canvas = canvas
        self.forces = forces
        self.events = events
        self.type = type
        self.collision_detection = collision_detection
        self.collision_type = collision_type
        self.collision_damping = collision_damping
        self.on_step_end = on_step_end
        
        # Repulsion parameters
        self.repel = repel
        self.repel_force = repel_force
        self.repel_radius = repel_radius

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
                point["live"] = True
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
                    self._step(point, all_points, all_attractor_points, time_step)

        elif self.type == "concurrent":
            for time_step in tqdm.tqdm(range(steps), desc="Time Step", position=0):
                for point in tqdm.tqdm(all_points, desc="Points", position=1, leave=False):
                    if not point["live"]:
                        continue
                    if "impulse" not in point:
                        point["impulse"] = (0, 0)

                    if "mass" not in point:
                        point["mass"] = 1.0

                    if "attractor" not in point:
                        point["attractor"] = 0.0
                    self._step(point, all_points, all_attractor_points, time_step)

                for function in self.on_step_end:
                    function(time_step)

    def _step(self, point, all_points, all_attractor_points, time_step):
        # Apply all regular forces
        for force in self.forces:
            force.apply(point, time_step, all_points=all_points)

        # Apply attractor forces
        for attractor_point in all_attractor_points:
            if attractor_point == point:
                continue
            attractor = Attractor.from_point(attractor_point)
            attractor.apply(point, time_step)

        # Calculate repulsion force from nearby lines
        if self.repel:
            repel_force_x, repel_force_y = self._calculate_repulsion_force(point, time_step)
            point["impulse"] = (
                point["impulse"][0] + repel_force_x * self.dt,
                point["impulse"][1] + repel_force_y * self.dt
            )

        start_x = point["x"]
        start_y = point["y"]

        event_collision = False
        if self.collision_detection:
            if self._check_collision(point["x"], point["y"],
                                   point["x"] + point["impulse"][0] * self.dt,
                                   point["y"] + point["impulse"][1] * self.dt,
                                   time_step):
                point["impulse"] = (-point["impulse"][0] * (1.0-self.collision_damping),
                                  -point["impulse"][1] * (1.0-self.collision_damping))
                if abs(point["impulse"][0]) < 0.0001 and abs(point["impulse"][1]) < 0.0001:
                    point["live"] = False
                event_collision = True

        # Handle events
        for event in self.events:
            for event_reason in event.on:
                if event_reason == "collision" and event_collision:
                    event.apply(point, time_step)
                elif event_reason == "near_point":
                    for point_to_check in all_points:
                        if point_to_check == point:
                            continue
                        if math.dist((point["x"], point["y"]),
                                   (point_to_check["x"], point_to_check["y"])) < event.distance:
                            event.apply(point, time_step, with_point=point_to_check)
                            break

        # Update position
        point["x"] += point["impulse"][0] * self.dt
        point["y"] += point["impulse"][1] * self.dt

        end_x = point["x"]
        end_y = point["y"]

        if time_step >= self.start_lines_at:
            self.canvas.line(start_x, start_y, end_x, end_y,
                           color=point["color"],
                           thickness=point["thickness"],
                           pid=point["pid"])
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
    
    def _calculate_line_point_distance(self, px, py, x1, y1, x2, y2):
        """Calculate the shortest distance from a point to a line segment"""
        A = px - x1
        B = py - y1
        C = x2 - x1
        D = y2 - y1

        dot = A * C + B * D
        len_sq = C * C + D * D

        if len_sq == 0:
            # x1 and x2 are the same point
            return math.sqrt(A * A + B * B)

        param = dot / len_sq

        if param < 0:
            # point is nearest to the start of the line segment
            return math.sqrt(A * A + B * B)
        elif param > 1:
            # point is nearest to the end of the line segment
            return math.sqrt((px - x2) * (px - x2) + (py - y2) * (py - y2))
        else:
            # normal case - project the point onto the line segment
            x = x1 + param * C
            y = y1 + param * D
            return math.sqrt((px - x) * (px - x) + (py - y) * (py - y))

    def _calculate_repulsion_force(self, point, current_time_step):
        """Calculate the repulsion force from nearby line segments"""
        if not self.repel:
            return (0, 0)

        cells = self._get_cells_for_line(
            point["x"] - self.repel_radius,
            point["y"] - self.repel_radius,
            point["x"] + self.repel_radius,
            point["y"] + self.repel_radius
        )

        total_force_x = 0
        total_force_y = 0

        for cell in cells:
            if cell in self.grid:
                for line in self.grid[cell]:
                    x1, y1, x2, y2, line_time_step = line
                    
                    # Only consider lines that are old enough
                    if current_time_step - line_time_step > self.collision_buffer_steps:
                        distance = self._calculate_line_point_distance(point["x"], point["y"], x1, y1, x2, y2)
                        
                        if distance < self.repel_radius:
                            # Calculate the closest point on the line
                            A = point["x"] - x1
                            B = point["y"] - y1
                            C = x2 - x1
                            D = y2 - y1
                            
                            dot = A * C + B * D
                            len_sq = C * C + D * D
                            param = max(0, min(1, dot / len_sq if len_sq != 0 else 0))
                            
                            closest_x = x1 + param * C
                            closest_y = y1 + param * D
                            
                            # Calculate direction from line to point
                            dir_x = point["x"] - closest_x
                            dir_y = point["y"] - closest_y
                            
                            # Normalize direction
                            length = math.sqrt(dir_x * dir_x + dir_y * dir_y)
                            if length > 0:
                                dir_x /= length
                                dir_y /= length
                                
                                # Force decreases with distance (inverse square law)
                                force_magnitude = self.repel_force * (1 - distance / self.repel_radius) ** 2
                                
                                total_force_x += dir_x * force_magnitude
                                total_force_y += dir_y * force_magnitude

        return (total_force_x, total_force_y)