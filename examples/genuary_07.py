import os
import cv2
import numpy as np
os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from penpal.generators.points import PointGrid, AddPointTool
from penpal.operators.color import ApplyColor
from penpal.operators.offset import Offset
from penpal.utils import Optimizations
from penpal.simulation.simulation import SetMass, SetImpulse, Simulation, SetAsAttractor
from penpal.simulation.constraint import IsometricConstraint
from penpal.simulation.rule import Rule
from penpal.operators.field import ApplyField
from penpal.operators.smooth import Smooth
from penpal.operators.flatten import Flatten
from penpal.operators.line_repel import LineRepel
from penpal.simulation.turbulence import Turbulence
from penpal.simulation.gravity import Gravity
from penpal.simulation.attractor import Attractor
from penpal.simulation.follow import FollowEdge
from penpal.filters.group import Group
from penpal.simulation.vortex import Vortex
from penpal.simulation.relax import Relax
from penpal.generators import ImageField
from penpal.simulation.drag import Drag, BorderDrag
from penpal.simulation.events import FlipMass
from penpal import Canvas, Render, SVG, GCode, SVGFont

canvas = Canvas(canvas_size_mm=(229.0, 305.0), paper_color="black", pen_color="white", respect_margin=True)
render = Render(canvas)

svg = SVG("examples/temp/SEDOV_KeyboardV1_PCB-F_Cu.svg")
svg.draw(canvas, canvas.margin, canvas.margin, scale=0.6, pen_width=0.35,  override_stroke_color="#1515ff")

svg = SVG("examples/temp/SEDOV_KeyboardV1_PCB-B_Cu.svg")
svg.draw(canvas, canvas.margin, canvas.margin+50, scale=0.6, pen_width=0.35,  override_stroke_color="#15ff15")

svg = SVG("examples/temp/SEDOV_KeyboardV1_PCB-B_Silkscreen.svg")
svg.draw(canvas, canvas.margin, canvas.margin+100, scale=0.6, pen_width=0.35,  override_stroke_color="#ff1515")

svg = SVG("examples/temp/SEDOV_KeyboardV1_PCB-F_Silkscreen.svg")
svg.draw(canvas, canvas.margin, canvas.margin+150, scale=0.6, pen_width=0.35,  override_stroke_color="#1515ff")

svg = SVG("examples/temp/SEDOV_KeyboardV1_PCB-B_Cu.svg")
svg.draw(canvas, canvas.margin-50, canvas.margin-130, scale=2.6, pen_width=0.35,  override_stroke_color="#ffffff")
#Optimizations.sort_lines(canvas)    
Optimizations.merge_lines(canvas, tolerance=0.1)

canvas.crop()
canvas.clear("points")
canvas.respect_margin = False

svg = SVG("signature25.svg")
svg.draw(canvas, canvas.canvas_size_mm[0] - canvas.margin - 48, canvas.canvas_size_mm[1] - canvas.margin+4, scale=1.5)
svg_text = SVGFont("alphabet.svg")
svg_text.draw(canvas, canvas.margin+72, 5, "GENUARY 07".upper(), scale=0.8, stroke_color=None, fill_color="#ffffff")


#render.save_video(folder="temp", name="output_genuary_06", fps=20)
render.render()
render.show()

gcode = GCode(canvas)
gcode.generate()
gcode.save("sedov_genuary_07.gcode")