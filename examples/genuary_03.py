import os
os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from penpal.generators.points import PointGrid
from penpal.operators.color import ApplyColor
from penpal.operators.merge import Merge
from penpal.operators.offset import Offset
from penpal.utils import Optimizations
from penpal.simulation.simulation import SetMass, SetImpulse, Simulation, SetAsAttractor
from penpal.simulation.turbulence import Turbulence
from penpal.simulation.attractor import Attractor
from penpal.simulation.drag import Drag
from penpal.simulation.constraint import MinImpulseConstraint, MaxImpulseConstraint
from penpal import Canvas, Render, SVG, GCode, SVGFont

canvas = Canvas(canvas_size_mm=(229.0, 305.0), paper_color="black", pen_color="white", respect_margin=True)
PointGrid(canvas, vspacing=20.0, hspacing=22.0, additional_margin=0.0).generate()
ApplyColor(canvas, color="#ffffff", chance=1.0)
ApplyColor(canvas, color="#ffff00", chance=0.1)
SetMass(canvas, mass=2.0)
SetAsAttractor(canvas, attractor=1.0)
SetImpulse(canvas, impulse=(0.0, 0.5))
canvas_b = canvas.clone()
SetMass(canvas_b, mass=10.0)
drag = Drag(canvas_b, drag=0.002)
turbulence = Turbulence(canvas_b, turbulence=0.001)
attractor = Attractor(attractor=(canvas.canvas_size_mm[0]/2, 0.0), strength=10.5)

Simulation(canvas,  forces=[turbulence]).simulate(500)
Simulation(canvas_b,  forces=[turbulence]).simulate(100)
Optimizations.merge_lines(canvas, tolerance=0.02)
Optimizations.merge_lines(canvas_b, tolerance=0.02)
Offset(canvas, count=2, offset_distance=1.0).apply()
#canvas = Merge(margin=0.0).apply(canvas, canvas_b)

canvas.respect_margin = False
# Add signature
print("Drawing signature")
svg = SVG("signature25.svg")
svg.draw(canvas, canvas.canvas_size_mm[0] - canvas.margin - 48, canvas.canvas_size_mm[1] - canvas.margin+4, scale=1.5)

svg_text = SVGFont("alphabet.svg")
svg_text.draw(canvas, canvas.margin+72, 5, "GENUARY 03".upper(), scale=0.8, stroke_color="#ffffff", fill_color=None)

# Render preview
render = Render(canvas)
render.render()
render.show()

# Generate GCode
gcode = GCode(canvas)
gcode.generate()
gcode.save("sedov_genuary_03.gcode")