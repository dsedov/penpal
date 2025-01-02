import os
os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from penpal.generators.points import PointGrid
from penpal.operators.color import ApplyColor
from penpal.utils import Optimizations
from penpal.simulation.simulation import SetMass, SetImpulse, Simulation, SetAsAttractor
from penpal.simulation.turbulence import Turbulence
from penpal.simulation.gravity import Gravity
from penpal.simulation.attractor import Attractor
from penpal.simulation.vortex import Vortex
from penpal.simulation.drag import Drag
from penpal import Canvas, Render, SVG, GCode, SVGFont

canvas = Canvas(canvas_size_mm=(229.0, 305.0), paper_color="black", pen_color="white", respect_margin=True)
PointGrid(canvas, vspacing=40.0, hspacing=44.0, additional_margin=0.0, hex_pattern=True).generate()
canvas.clear("points", chance=0.9)
ApplyColor(canvas, color="#ffffff", chance=1.0)
ApplyColor(canvas, color="#ffff00", chance=0.1)
ApplyColor(canvas, color="#ff0000", chance=0.1)

SetMass(canvas, mass=2.0)
SetAsAttractor(canvas, attractor=1.0)
SetImpulse(canvas, impulse=(0.0, 0.5))
drag = Drag(canvas, drag=0.002)

Simulation(canvas,  forces=[], type="concurrent").simulate(15000)
Optimizations.merge_lines(canvas, tolerance=0.02)

canvas.crop()
canvas.clear("points")
canvas.respect_margin = False

svg = SVG("signature25.svg")
svg.draw(canvas, canvas.canvas_size_mm[0] - canvas.margin - 48, canvas.canvas_size_mm[1] - canvas.margin+4, scale=1.5)
svg_text = SVGFont("alphabet.svg")
svg_text.draw(canvas, canvas.margin+72, 5, "GENUARY 04".upper(), scale=0.8, stroke_color=None, fill_color="#ffffff")

render = Render(canvas)
render.render()
render.show()

gcode = GCode(canvas)
gcode.generate()
gcode.save("sedov_genuary_04.gcode")