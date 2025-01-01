from dataclasses import dataclass
from itertools import cycle
from typing import List, Tuple
import math

@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    mass: float

@dataclass
class Attractor:
    x: float
    y: float
    mass: float

class GravitySimulation:
    def __init__(self, canvas, max_steps=200, attractors=[]):
        self.canvas = canvas

        self.max_steps = max_steps
        self.width, self.height = canvas.canvas_size_mm
        
        # Physics constants
        self.G = 0.5  # Gravitational constant
        self.dt = 0.1  # Time step
        
        # Initialize attractors (you can modify these positions)
        self.attractors = attractors

    def calculate_force(self, particle: Particle, attractor: Attractor) -> Tuple[float, float]:
        dx = attractor.x - particle.x
        dy = attractor.y - particle.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Avoid division by zero and extreme forces at very small distances
        distance = max(distance, 1.0)
        
        force = (self.G * attractor.mass) / (distance * distance)
        return (force * dx / distance, force * dy / distance)

    def simulate_particle(self, particle) -> List[Tuple[float, float]]:

        path = [(particle.x, particle.y)]
        
        for _ in range(self.max_steps):
            fx = fy = 0
            
            # Calculate total force from all attractors
            for attractor in self.attractors:
                force_x, force_y = self.calculate_force(particle, attractor)
                fx += force_x
                fy += force_y
            
            # Update velocity and position
            particle.vx += fx * self.dt
            particle.vy += fy * self.dt
            particle.x += particle.vx * self.dt
            particle.y += particle.vy * self.dt
            
            # Add point to path
            path.append((particle.x, particle.y))
            
            # Stop if particle goes out of bounds
            if (particle.x < self.canvas.margin or particle.x > self.width-self.canvas.margin or 
                particle.y < self.canvas.margin or particle.y > self.height-self.canvas.margin):
                break
        
        return path

    def draw_path(self, path: List[Tuple[float, float]], color="white", thickness=0.5):
        """Draw a single particle's path"""
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            self.canvas.line(x1, y1, x2, y2, color=color, thickness=thickness)

    def simulate(self, particle_list=None, colors=None):
        """Generate and draw all paths"""
        if colors is None:
            colors = ["white"]  # Default to white if no colors specified
        color_cycle = cycle(colors)

        for particle in particle_list:
            color = next(color_cycle)
            path = self.simulate_particle(particle)
            self.draw_path(path, color=color)

    def add_attractor(self, x: float, y: float, mass: float = 500):
        """Add a new attractor at the specified position"""
        self.attractors.append(Attractor(x=x, y=y, mass=mass))

