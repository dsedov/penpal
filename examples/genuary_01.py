import os
import numpy as np
import random

os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from penpal import Canvas, Render, SVG, GCode
from penpal import VectorField
canvas = Canvas(canvas_size_mm=(229.0, 305.0), paper_color="black", pen_color="white")

margin = 15.0

plotted_width_mm = canvas.canvas_size_mm[0] - margin*2
plotted_height_mm = canvas.canvas_size_mm[1] - margin*2

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

field = VectorField(
    scale=0.02,        # Controls the "zoom level" of the noise
    octaves=5,        # More octaves = more detail
    persistence=0.5,  # How much each octave contributes
    blur_radius=1.0   # Amount of smoothing
)

for y in np.arange(margin, plotted_height_mm, box_size_y):
    for x in np.arange(margin, plotted_width_mm, box_size_x):
        dx, dy = field.get_vector(x, y)
        if random.random() < chance_of_skip:
            continue
        canvas.box(
            x + total_x_offset + dx * field_scale + box_margin, 
            y + total_y_offset + dy * field_scale + box_margin,  
            box_size_x - box_margin*2, 
            box_size_y - box_margin*2, 
            thickness=0.6,
            filled=random.random() < chance_of_fill)
        
        noise += noise_step
        scale += scale_step
    chance_of_skip += chance_of_skip_increase
    chance_of_fill += chance_of_fill_increase


render = Render(canvas)
render.render()
render.show()


gcode = GCode(canvas)
gcode.generate()
gcode.save("genuary_01.gcode")
