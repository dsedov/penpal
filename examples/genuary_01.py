import os
import numpy as np
import random

os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from penpal import Canvas, Render, SVG, GCode, SVGFont

canvas = Canvas(canvas_size_mm=(229.0, 305.0), paper_color="black", pen_color="white")

# Generate artwork
box_size = 19.0
box_margin = 0.5
num_boxes_x = int(canvas.plottable_size[0] / (box_size + box_margin))    
num_boxes_y = int(canvas.plottable_size[1] / (box_size + box_margin))
box_size_x = (num_boxes_x * box_size + (num_boxes_x - 1) * box_margin) / num_boxes_x
box_size_y = (num_boxes_y * box_size + (num_boxes_y - 1) * box_margin) / num_boxes_y
noise = 0.0
noise_step = 0.0005
scale = 0.8
scale_step = 0.16
chance_of_skip = 0.25
chance_of_skip_increase = 0.002
chance_of_fill = 1.0
chance_of_fill_increase = 0.03
chance_of_horizonal = 0.95

canvas.translate(2,0)
canvas.push()
for y in np.arange(canvas.top_left[1], canvas.bottom_right[1] - box_size_y, box_size_y):
    for x in np.arange(canvas.top_left[0], canvas.bottom_right[0] - box_size_x, box_size_x):

        canvas.pop()
        canvas.translate(x + box_margin + box_size_x/2, y + box_margin + box_size_y/2)
        canvas.scale(1.0)#, random.uniform(1.0, dy*2))
        is_outline = False if random.random() > chance_of_skip else True
        canvas.box(
            -box_size_x/2 - box_margin, 
            -box_size_y/2 - box_margin, 
            box_size_x - box_margin*2, 
            box_size_y - box_margin*2, 
            color="#ffffff",
            thickness=0.6,
            align_fill_to_edges=True,
            outline=is_outline,
            fill_direction= "vertical" if random.random() < chance_of_horizonal else "horizontal",
            fill_density=0.5 * scale,
            filled= not is_outline and random.random() < chance_of_fill)
    scale -= scale_step
    chance_of_skip += chance_of_skip_increase
    chance_of_fill += chance_of_fill_increase
canvas.pop()



# Add signature
print("Drawing signature")
svg = SVG("signature25.svg")
svg.draw(canvas, canvas.canvas_size_mm[0] - canvas.margin - 48, canvas.canvas_size_mm[1] - canvas.margin+4, scale=1.5)

svg_text = SVGFont("alphabet.svg")
svg_text.draw(canvas, canvas.margin+72, 5, "GENUARY 01".upper(), scale=0.8, stroke_color="#ffffff", fill_color="#ffffff")

# Render preview
render = Render(canvas)
render.render()
render.show()

# Generate GCode
gcode = GCode(canvas)
gcode.generate()
gcode.save("sedov_genuary_01.gcode")
