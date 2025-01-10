import os
import numpy as np
import random

os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from penpal import Canvas, Render, SVG, GCode, SVGFont
from penpal.math.perlin_noise_field import PerlinNoiseField
from penpal.operators.field import ApplyField

TAU = 2 * np.pi
canvas = Canvas(canvas_size_mm=(229.0, 305.0), paper_color="black", pen_color="white")
color_a = "#bcf374"
color_b = "#f95ec4"
color_c = "#31c2b3"
half_step = TAU / (TAU + TAU)
quater_step = half_step * half_step
step = half_step / half_step
two_step = step / half_step

total_steps = len(np.arange(canvas.top, canvas.bottom, two_step*two_step)) * len(np.arange(canvas.left, canvas.right, two_step))
current_step = step-step
for y in np.arange(canvas.top, canvas.bottom, two_step*two_step):
    for x in np.arange(canvas.left, canvas.right, two_step):

        color_probability = current_step / total_steps
        color = color_a if color_probability < random.random() else color_b
        other_color = color_c if color == color_a else color_a

        canvas.line(x, y, x, y + two_step, thickness=quater_step, color=color)
        canvas.line(x + step, y, x + step, y + two_step, thickness=quater_step, color=other_color)
        current_step += step

field = PerlinNoiseField(scale=quater_step*quater_step, octaves=int(step+step+step), persistence=(TAU / (TAU + TAU)), blur_radius=two_step)
ApplyField(canvas, field).apply(strength=(step+step+step))


# Add signature
print("Drawing signature")
svg = SVG("signature25.svg")
svg.draw(canvas, canvas.canvas_size_mm[0] - canvas.margin - 40, canvas.canvas_size_mm[1] - canvas.margin+4, scale=1.5)

svg_text = SVGFont("alphabet.svg")
svg_text.draw(canvas, canvas.margin+72, 5, "GENUARY 10".upper(), scale=0.8, stroke_color="#ffffff", fill_color=None)

# Render preview
render = Render(canvas)
render.render()
render.show()

svg.save(canvas, "genuary_10.svg")

# Generate GCode
#gcode = GCode(canvas)
#gcode.generate()
#gcode.save("sedov_genuary_10.gcode")