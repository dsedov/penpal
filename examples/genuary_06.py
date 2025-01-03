import os
import cv2
os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from penpal.generators.points import PointGrid
from penpal.operators.color import ApplyColor
from penpal.utils import Optimizations, save_as_video
from penpal.simulation.simulation import SetMass, SetImpulse, Simulation, SetAsAttractor
from penpal.simulation.constraint import IsometricConstraint
from penpal.operators.field import ApplyField
from penpal.simulation.turbulence import Turbulence
from penpal.simulation.gravity import Gravity
from penpal.simulation.attractor import Attractor
from penpal.simulation.vortex import Vortex
from penpal.simulation.relax import Relax
from penpal.generators import ImageField
from penpal.simulation.drag import Drag, BorderDrag
from penpal.simulation.events import FlipMass
from penpal import Canvas, Render, SVG, GCode, SVGFont

canvas = Canvas(canvas_size_mm=(229.0, 305.0), paper_color="black", pen_color="white", respect_margin=True)
PointGrid(canvas, vspacing=5.0, hspacing=5.0, additional_margin=0.0, hex_pattern=True).generate()

SetImpulse(canvas, impulse=(0.0, 0.0))
landscape_image_field = ImageField(canvas, "landscape.jpg", dpi=300)
#ApplyField(canvas, field=landscape_image_field).apply(strength=-3.0)
landscape_image_field.threshold(0.1, 0.5)
landscape_image_field.gamma(0.4)
turbulence = Turbulence(canvas, turbulence=0.1)
#ApplyColor(canvas, color="#ffffff", chance=1.0)
#ApplyColor(canvas, color="#ffff00", chance=0.1)
#ApplyColor(canvas, color="#ff0000", chance=0.1)
ApplyColor(canvas, color=["#252525", "#454545","#ffffff"], field=landscape_image_field)
SetMass(canvas, mass=1.0, field=landscape_image_field)
SetMass(canvas, mass=2.0, mode="add")
#SetAsAttractor(canvas, attractor=1.0, chance=0.1)
isometric_constraint = IsometricConstraint(canvas,strength=0.5, after_time=70)
border_drag = BorderDrag(canvas, drag=1.0)
drag = Drag(canvas, field=landscape_image_field.inversed(), drag=0.3, before_time=70)
drag2 = Drag(canvas, drag=0.002, before_time=70)
freeze = Drag(canvas, drag=1.0, after_time=70, before_time=72)
relax = Relax(canvas, strength=0.1, radius=10.0, before_time=70)
vortex = Vortex(canvas.canvas_size_mm[0]/2, canvas.canvas_size_mm[1]/2, strength=0.1, after_time=70)
snapshot_images = []
def enable_attractors(time_step):
    if time_step == 70:
        SetAsAttractor(canvas, attractor=1.0, chance=0.5)
        #SetImpulse(canvas, impulse=(0.0, -1.0))
        SetMass(canvas, mass=1.0)

def snapshot_image(time_step):
    r = Render(canvas, dpi=150)
    r.render(points=True)
    snapshot_images.append(r.image)
    r.image.save(f"temp/_{time_step}.png")

Simulation(canvas,  forces=[ relax, drag2, turbulence, isometric_constraint, border_drag], events=[], dt=0.1, start_lines_at=70, type="concurrent", 
           collision_detection=True, 
           collision_type="line", 
           collision_damping=1.0,
           collision_flip_mass=False,
           on_step_end=[snapshot_image, enable_attractors]
           ).simulate(250)

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