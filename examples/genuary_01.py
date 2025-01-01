import os
import numpy as np
import random
import math
os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from dataclasses import dataclass
from typing import List, Tuple
from penpal.utils import Optimizations

from penpal import Canvas, Render, SVG, GCode

canvas = Canvas(canvas_size_mm=(229.0, 305.0), paper_color="black", pen_color="white")

margin = 15.0

plotted_width_mm = canvas.canvas_size_mm[0] - margin*2
plotted_height_mm = canvas.canvas_size_mm[1] - margin*2

@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float

@dataclass
class Attractor:
    x: float
    y: float
    mass: float

class GravitationalArt:
    def __init__(self, canvas, num_particles=50, max_steps=200, default_mass=200, mass_range=100):
        self.canvas = canvas
        self.num_particles = num_particles
        self.max_steps = max_steps
        self.width, self.height = canvas.canvas_size_mm
        
        # Physics constants
        self.G = 0.5  # Gravitational constant
        self.dt = 0.1  # Time step
        
        # Initialize attractors (you can modify these positions)
        self.attractors = [
            Attractor(x=self.width * 0.3, y=self.height * 0.3, mass=default_mass + random.uniform(-mass_range, mass_range)),
            Attractor(x=self.width * 0.7, y=self.height * 0.7, mass=default_mass + random.uniform(-mass_range, mass_range)),
            #Attractor(x=self.width * 0.3, y=self.height * 0.7, mass=default_mass + random.uniform(-mass_range, mass_range)),
            #Attractor(x=self.width * 0.7, y=self.height * 0.3, mass=default_mass + random.uniform(-mass_range, mass_range)),

        ]

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
            if (particle.x < margin or particle.x > self.width-margin or 
                particle.y < margin or particle.y > self.height-margin):
                break
        
        return path

    def draw_path(self, path: List[Tuple[float, float]], color="white", thickness=0.5):
        """Draw a single particle's path"""
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            self.canvas.line(x1, y1, x2, y2, color=color, thickness=thickness)

    def generate_art(self, particle_list=None, colors=None):
        """Generate and draw all paths"""
        if colors is None:
            colors = ["white"]  # Default to white if no colors specified
        
        for particle, color in zip(particle_list, colors):
            path = self.simulate_particle(particle)
            self.draw_path(path, color=color)

    def add_attractor(self, x: float, y: float, mass: float = 500):
        """Add a new attractor at the specified position"""
        self.attractors.append(Attractor(x=x, y=y, mass=mass))


art = GravitationalArt(canvas, max_steps=100000, default_mass=8, mass_range=0.01)
possible_colors = ["#ffffff", "#2bc76d", "#2b5bc7"]
step = 11
chance_to_skip = 0.0

print("Generating art")
for x in np.arange(margin, plotted_width_mm+margin, step):
    is_odd = True
    for y in np.arange(margin, plotted_height_mm+margin, step):
        if random.random() > chance_to_skip:
            px = x if is_odd else x+step/2
            py = y
            # check if point near attractor
            for attractor in art.attractors:
                if math.sqrt((px-attractor.x)**2 + (py-attractor.y)**2) < 10:
                    continue
            impulse_x = 0.2 #random.uniform(0.2, 0.3)
            art.generate_art(particle_list=[Particle(x=px, y=py, vx=impulse_x, vy=-0.0)], colors=[ random.choice(possible_colors) ]) 
        #is_odd = not is_odd
    break

print("Drawing signature")
svg = SVG("signature25.svg")
svg.draw(canvas, margin, 10, scale=0.5, flip_y=True)

print("Optimizing")
print(f"Before: {len(canvas.draw_stack)}")
Optimizations.merge_lines(canvas, tolerance=0.005)
print(f"After: {len(canvas.draw_stack)}")

# Render preview
print("Rendering preview")
render = Render(canvas)
render.render()
render.show()

# Generate GCode
print("Generating GCode")
gcode = GCode(canvas, draw_speed=5000)
gcode.generate()
gcode.save("genuary_01.gcode")
