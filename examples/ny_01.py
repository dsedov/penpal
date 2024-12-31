import os
import numpy as np
import random

os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from penpal import Canvas, Render, SVG, GCode
from penpal import VectorField

big_black_paper = (229.0, 305.0)
small_black_paper = (152.0, 203.0)

canvas = Canvas(canvas_size_mm=small_black_paper, paper_color="black", pen_color="white")
canvas.tolerance = 0.3
margin = 15.0

plotted_width_mm = canvas.canvas_size_mm[0] - margin*2
plotted_height_mm = canvas.canvas_size_mm[1] - margin*2


# Generate artwork
total_x_offset = 0.0
total_y_offset = 0.0
box_size = 20.0
box_margin = 2.0
num_boxes_x = int(plotted_width_mm / (box_size + box_margin))
num_boxes_y = int(plotted_height_mm / (box_size + box_margin))
box_size_x = (num_boxes_x * box_size + (num_boxes_x - 1) * box_margin) / num_boxes_x
box_size_y = (num_boxes_y * box_size + (num_boxes_y - 1) * box_margin) / num_boxes_y
noise = 0.0
noise_step = 0.0005
scale = 3
scale_step = 0.5
chance_of_skip = 0.1
chance_of_skip_increase = 0.002
chance_of_fill = -0.01
chance_of_fill_increase = 0.03
field_scale = 2.0  


# Add signature
svg = SVG("ny.svg")
svg.draw(canvas, 0, 207, scale=0.35, flip_y=True)

svg = SVG("signature25.svg")
svg.draw(canvas, 110, 10, scale=0.35, flip_y=True)

# Render preview
render = Render(canvas)
render.render()
render.show()

# Generate GCode
gcode = GCode(canvas)
gcode.draw_speed = 1000
gcode.generate(shake_pen=0.1)
gcode.save("genuary_01.gcode")
