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
from penpal.operators import DifferentialGrowth, Noise


canvas = Canvas(canvas_size_mm=(229.0, 305.0), paper_color="black", pen_color="white", respect_margin=True)
render = Render(canvas)

temp_canvas = Canvas(canvas_size_mm=(229.0, 305.0), paper_color="black", pen_color="white", respect_margin=False)

# Start with more initial points
temp_canvas.circle(
    temp_canvas.canvas_size_mm[0]/2, 
    temp_canvas.canvas_size_mm[1]/2, 
    50, 
    step_size=2.0,  # Smaller step size = more points
    color="#ffffff", 
    thickness=0.5
)
dg = DifferentialGrowth(
    temp_canvas,
    split_distance=5.0,
    repulsion_radius=10.0,
    repulsion_strength=1.2,      # Much stronger outward force
    attraction_strength=0.4,     # Keep moderate attraction to maintain structure
    alignment_strength=0.1,      # Less smoothing to allow more dramatic growth
    damping=0.8,                # More aggressive movement
    relax_iterations=2
)

# More iterations for more dramatic effect
for _ in range(50):  # Increased iterations
    dg.apply()

canvas.merge_with(temp_canvas)

#Smooth(canvas, strength=0.5, iterations=2, contraction=0.01).apply()
#Optimizations.sort_lines(canvas)    
#Optimizations.merge_lines(canvas, tolerance=0.1)

canvas.clear("points")
canvas.respect_margin = False

svg = SVG("signature25.svg")
svg.draw(canvas, canvas.canvas_size_mm[0] - canvas.margin - 48, canvas.canvas_size_mm[1] - canvas.margin+4, scale=1.5)
svg_text = SVGFont("alphabet.svg")
svg_text.draw(canvas, canvas.margin+72, 5, "GENUARY 08".upper(), scale=0.8, stroke_color=None, fill_color="#ffffff")


#render.save_video(folder="temp", name="output_genuary_06", fps=20)
render.render()
render.show()

gcode = GCode(canvas)
gcode.generate()
gcode.save("sedov_genuary_06.gcode")