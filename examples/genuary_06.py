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

# Rules and fields
add_point_tool = AddPointTool(canvas)
follow_edge = FollowEdge(canvas, "landscape.jpg", angle_range=20, step_size=5, dpi=50)
isometric_constraint = IsometricConstraint(canvas, angle_degrees=30, threshold=1.0, strength=0.5)
return_to_original_y = Rule(canvas, Rule.rule_to_return_to_original_y, strength=0.5)

# Add seed points
for y in np.arange(canvas.top_left[1], canvas.bottom_right[1], 5):
    add_point_tool.add_point(canvas.top_left[0], y)

# Set initial conditions
SetImpulse(canvas, impulse=(0.0, 0.0))
ApplyColor(canvas, color="#ffffff", chance=1.0)
SetMass(canvas, mass=2.0)



def snapshot_image(time_step):
    render.snapshot_image(time_step, every=5, save=True, folder="temp")
sim_a = Simulation(canvas,  forces=[ follow_edge, isometric_constraint, return_to_original_y], events=[], dt=0.1, 
           start_lines_at=0, 
           type="concurrent", 
           collision_detection=False, 
           collision_type="line", 
           collision_damping=1.0,
           collision_flip_mass=False,
           repel=True,
           repel_force=2.0,
           repel_radius=15.0,
           on_step_end=[]
           )
sim_a.simulate(900)
canvas.clear("points")

Optimizations.sort_lines(canvas)    
Optimizations.merge_lines(canvas, tolerance=0.1)

Smooth(canvas, strength=0.5, iterations=2, contraction=0.01).apply()
groups_medium = Group(canvas).where(lambda op: op["type"] == "line" and op["y1"] < canvas.bottom and op["y1"] > canvas.top + 190).expand_pids()
groups_small  = Group(canvas).where(lambda op: op["type"] == "line" and op["y1"] < canvas.bottom and op["y1"] > canvas.top + 150).expand_pids()
groups_small.remove_pids(groups_medium.all_pids())
groups_medium.remove_pids(groups_small.all_pids())
Flatten(canvas, axis="x", strength=1.0, group=groups_medium).apply()

Smooth(canvas, strength=0.5, iterations=4, group=groups_medium, contraction=0.01).apply()
Offset(canvas, offset_distance=0.4, count=12, group=groups_medium).apply()
Offset(canvas, offset_distance=0.5, count=3, group=groups_small).apply()

#Optimizations.sort_lines(canvas)    
#Optimizations.merge_lines(canvas, tolerance=0.1)

canvas.crop()
canvas.clear("points")
canvas.respect_margin = False

svg = SVG("signature25.svg")
svg.draw(canvas, canvas.canvas_size_mm[0] - canvas.margin - 48, canvas.canvas_size_mm[1] - canvas.margin+4, scale=1.5)
svg_text = SVGFont("alphabet.svg")
svg_text.draw(canvas, canvas.margin+72, 5, "GENUARY 06".upper(), scale=0.8, stroke_color=None, fill_color="#ffffff")


#render.save_video(folder="temp", name="output_genuary_06", fps=20)
render.render()
render.show()

gcode = GCode(canvas)
gcode.generate()
gcode.save("sedov_genuary_06.gcode")