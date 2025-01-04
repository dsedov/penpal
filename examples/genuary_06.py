import os
import cv2
import numpy as np
os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from penpal.generators.points import PointGrid, AddPointTool
from penpal.operators.color import ApplyColor
from penpal.utils import Optimizations, save_as_video
from penpal.simulation.simulation import SetMass, SetImpulse, Simulation, SetAsAttractor
from penpal.simulation.constraint import IsometricConstraint
from penpal.operators.field import ApplyField
from penpal.simulation.turbulence import Turbulence
from penpal.simulation.gravity import Gravity
from penpal.simulation.attractor import Attractor
from penpal.simulation.follow import FollowEdge
from penpal.simulation.vortex import Vortex
from penpal.simulation.relax import Relax
from penpal.generators import ImageField
from penpal.simulation.drag import Drag, BorderDrag
from penpal.simulation.events import FlipMass
from penpal import Canvas, Render, SVG, GCode, SVGFont

canvas = Canvas(canvas_size_mm=(229.0, 305.0), paper_color="black", pen_color="white", respect_margin=True)
add_point_tool = AddPointTool(canvas)
relax = Relax(canvas, strength=4.0, radius=20.0, min_distance=1.0)
turbulence = Turbulence(canvas, turbulence=0.1)
follow_edge = FollowEdge(canvas, "landscape.jpg", angle_range=45, step_size=5, dpi=50)
follow_edge_back = FollowEdge(canvas, "landscape.jpg", angle_range=45, step_size=-5, dpi=50)
isometric_constraint = IsometricConstraint(canvas, angle_degrees=30, threshold=1.0, strength=0.5)
border_drag = BorderDrag(canvas, drag=1.0)
drag = Drag(canvas, drag=0.001 )
snapshot_images = []
def snapshot_image(time_step):
    r = Render(canvas, dpi=150)
    r.render(points=True)
    snapshot_images.append(r.image)
    r.image.save(f"temp/_{time_step}.png")




for y in np.arange(canvas.top_left[1], canvas.bottom_right[1], 5):
    add_point_tool.add_point(canvas.top_left[0], y)

SetImpulse(canvas, impulse=(0.0, 0.0))
ApplyColor(canvas, color="#ffffff", chance=1.0)

SetMass(canvas, mass=2.0)
sim_a = Simulation(canvas,  forces=[ follow_edge,  relax], events=[], dt=0.1, 
           start_lines_at=0, 
           type="concurrent", 
           collision_detection=False, 
           collision_type="line", 
           collision_damping=1.0,
           collision_flip_mass=False,
           on_step_end=[snapshot_image]
           )
sim_a.simulate(900)

canvas.clear("points")
for y in np.arange(canvas.bottom_right[1], canvas.top_left[1], -5):
    add_point_tool.add_point(canvas.bottom_right[0], y)

SetImpulse(canvas, impulse=(0.0, 0.0))
ApplyColor(canvas, color="#ffffff", chance=1.0)
SetMass(canvas, mass=2.0)
sim_b = Simulation(canvas,  forces=[ follow_edge_back,  relax ], events=[], dt=0.1, 
           start_lines_at=0, 
           type="concurrent", 
           collision_detection=False, 
           collision_type="line", 
           collision_damping=1.0,
           collision_flip_mass=False,
           on_step_end=[snapshot_image]
           )
sim_b.grid = {
    cell: [(x1, y1, x2, y2, 0) for x1, y1, x2, y2, _ in lines] 
    for cell, lines in sim_a.grid.items()
} # ensure that we retain collision grid from sim_a and reset time stemps on those lines
sim_b.simulate(900)
canvas.clear("points")


if len(snapshot_images) > 0:
    # add reverse list to the 
    #snapshot_images.extend(reversed(snapshot_images))
    snapshot_images = list(reversed(snapshot_images)) + snapshot_images
    save_as_video(snapshot_images, "output_genuary_06.mp4", fps=20)
    snapshot_images[0].save('output_genuary_06.gif',
    save_all=True,           # This tells PIL to save all frames
    append_images=snapshot_images[1:], # This adds all other images after the first
    duration=50,             # 50ms between frames = 20fps
    loop=0                   # 0 means loop forever)
    )
Optimizations.sort_lines(canvas)    
Optimizations.merge_lines(canvas, tolerance=0.02)

canvas.crop()
canvas.clear("points")
canvas.respect_margin = False

svg = SVG("signature25.svg")
svg.draw(canvas, canvas.canvas_size_mm[0] - canvas.margin - 48, canvas.canvas_size_mm[1] - canvas.margin+4, scale=1.5)
svg_text = SVGFont("alphabet.svg")
svg_text.draw(canvas, canvas.margin+72, 5, "GENUARY 05".upper(), scale=0.8, stroke_color=None, fill_color="#ffffff")

render = Render(canvas)
render.render()
render.show()

gcode = GCode(canvas)
gcode.generate()
gcode.save("sedov_genuary_06.gcode")