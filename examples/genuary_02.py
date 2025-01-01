import os
import numpy as np
import random
import math
os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from dataclasses import dataclass
from typing import List, Tuple
from penpal.utils import Optimizations
from penpal.generators.points import PopulatePoints

from penpal import Canvas, Render, SVG, GCode, SVGFont, Noise, Subdivide, Field, PerlinNoiseField

canvas = Canvas(canvas_size_mm=(229.0, 305.0), paper_color="black", pen_color="white")
margin = 15.0
canvas.margin = margin
plotted_width_mm = canvas.canvas_size_mm[0] - margin*2
plotted_height_mm = canvas.canvas_size_mm[1] - margin*2

name = "genuary_02"
## ART BEGINS HERE

svg_font = SVGFont("alphabet.svg")
svg_font.draw(canvas, 8, 260, "Hello World".upper(), scale=2.8, stroke_color=None, fill_color="white")

# populating points
print("Populating points")
populate_points = PopulatePoints(canvas)
points = populate_points.generate(density=0.5)
print(f"Points: {len(points)}")
canvas.clear()
from penpal.simulation.gravity import GravitySimulation, Attractor, Particle

attractors = []
particles = []
chance_of_particle = 0.02
for point in points:
    if random.random() < chance_of_particle:
        particles.append(Particle(x=point[0], y=point[1], vx=0.0, vy=-0.2, mass=1.0))

attractors = [
    Attractor(x=plotted_width_mm * 0.3, y=plotted_height_mm * 0.3, mass=8),
    #Attractor(x=plotted_width_mm * 0.7, y=plotted_height_mm * 0.7, mass=20),
]
gravity_simulation = GravitySimulation(canvas, max_steps=20000, attractors=attractors)   
gravity_simulation.simulate(particle_list=particles, colors=["red", "green"])

## ART ENDS HERE



#svg = SVG("shape.svg")
#svg.draw(canvas, 10, 170, scale=5.0, flip_y=True, pen_width=2.5)


# Subdivide
#print("Subdividing")
#subdivide = Subdivide(canvas, min_length=0.2)
#subdivide.apply()

print("Adding field")
perlin_noise_field = PerlinNoiseField(scale=0.1, octaves=3, persistence=0.5, blur_radius=5.0)
Optimizations.merge_lines(canvas, tolerance=0.005)
field = Field(canvas, perlin_noise_field)
field.apply(2.0)
svg_font.draw(canvas, 8, 8, "Hello World".upper(), scale=2.8, stroke_color=None, fill_color="white")
print("Drawing signature")
svg = SVG("signature25.svg")
svg.draw(canvas, margin, 10, scale=1.0)


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
gcode.save(f"{name}.gcode")
