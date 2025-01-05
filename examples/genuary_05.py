import os
import cv2
os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from penpal.generators.points import PointGrid
from penpal.operators.color import ApplyColor
from penpal.utils import Optimizations
from penpal.simulation.simulation import SetMass, SetImpulse, Simulation, SetAsAttractor
from penpal.simulation.constraint import IsometricConstraint
from penpal.simulation.turbulence import Turbulence
from penpal.simulation.gravity import Gravity
from penpal.simulation.attractor import Attractor
from penpal.simulation.vortex import Vortex
from penpal.simulation.drag import Drag
from penpal.simulation.events import FlipMass
from penpal import Canvas, Render, SVG, GCode, SVGFont

canvas = Canvas(canvas_size_mm=(229.0, 305.0), paper_color="black", pen_color="white", respect_margin=True)
render = Render(canvas)
PointGrid(canvas, vspacing=5.0, hspacing=5.5, additional_margin=0.0, hex_pattern=True).generate()
canvas.clear("points", chance=0.9)
ApplyColor(canvas, color="#ffffff", chance=1.0)
ApplyColor(canvas, color="#ffff00", chance=0.1)
ApplyColor(canvas, color="#ff0000", chance=0.1)

SetMass(canvas, mass=4.0)
SetMass(canvas, mass=-4.0, chance=0.5)
SetImpulse(canvas, impulse=(10, 10), randomize=True)
SetAsAttractor(canvas, attractor=1.0)
isometric_constraint = IsometricConstraint(canvas, angle_degrees=30, threshold=1.0, strength=1.0)

def snapshot_image(time_step):
    render.snapshot_image(time_step, every=1, save=True, folder="temp")
Simulation(canvas,  forces=[isometric_constraint], events=[], dt=0.1, start_lines_at=0, type="concurrent", 
           collision_detection=True, 
           collision_type="line", 
           collision_damping=1.0,
           collision_flip_mass=False,
           on_step_end=[snapshot_image]
           ).simulate(70)

Optimizations.sort_lines(canvas)    
Optimizations.merge_lines(canvas, tolerance=0.02)

canvas.crop()
canvas.clear("points")
canvas.respect_margin = False

svg = SVG("signature25.svg")
svg.draw(canvas, canvas.canvas_size_mm[0] - canvas.margin - 48, canvas.canvas_size_mm[1] - canvas.margin+4, scale=1.5)
svg_text = SVGFont("alphabet.svg")
svg_text.draw(canvas, canvas.margin+72, 5, "GENUARY 05".upper(), scale=0.8, stroke_color=None, fill_color="#ffffff")

render.save_video(folder="temp", name="output_genuary_05", fps=20)
render.render()
render.show()

gcode = GCode(canvas)
gcode.generate()
gcode.save("sedov_genuary_05.gcode")