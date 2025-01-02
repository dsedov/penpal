import os
import numpy as np
import random
os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from penpal.utils import Optimizations
from penpal.generators.points import PointGrid
from penpal.operators.color import ApplyColor
from penpal.simulation.simulation import SetMass, SetImpulse, Simulation, SetAsAttractor
from penpal.simulation.turbulence import Turbulence
from penpal.simulation.attractor import Attractor
from penpal.simulation.drag import Drag
from penpal import Canvas, Render, SVG, GCode, SVGFont

canvas = Canvas(canvas_size_mm=(229.0, 305.0), paper_color="black", pen_color="white")
canvas.respect_margin = True
canvas.push()
canvas.translate(2,0)

PointGrid(canvas, vspacing=30.0, hspacing=32.0, additional_margin=0.0).generate()
canvas.pop()
ApplyColor(canvas, color="#ffffff", chance=1.0)
ApplyColor(canvas, color="#ff0000", chance=0.1)
SetMass(canvas, mass=1.0)
SetAsAttractor(canvas, attractor=1.0)
SetImpulse(canvas, impulse=(0.0, 0.5))
drag = Drag(canvas, drag=0.002)


turbulence = Turbulence(canvas, turbulence=0.01)
attractor = Attractor(attractor=(canvas.canvas_size_mm[0]/2, 0.0), strength=10.5)
Simulation(canvas,
           forces=[turbulence, attractor, drag],
           ).simulate(1000)






canvas.respect_margin = False
# Add signature
print("Drawing signature")
svg = SVG("signature25.svg")
svg.draw(canvas, canvas.canvas_size_mm[0] - canvas.margin - 48, canvas.canvas_size_mm[1] - canvas.margin+4, scale=1.5)

svg_text = SVGFont("alphabet.svg")
svg_text.draw(canvas, canvas.margin+72, 5, "GENUARY 02".upper(), scale=0.8, stroke_color="#ffffff", fill_color="#ffffff")

# Optimize
#optimizations = Optimizations()
#optimizations.merge_lines(canvas, tolerance=0.02)

# Render preview
render = Render(canvas)
render.render()
render.show()

# Generate GCode
gcode = GCode(canvas)
gcode.generate()
gcode.save("___sedov_genuary_02.gcode")