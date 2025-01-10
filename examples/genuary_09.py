import os
import numpy as np
import random

os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from penpal import Canvas, Render, SVG, GCode, SVGFont

canvas = Canvas(canvas_size_mm=(229.0, 305.0), paper_color="black", pen_color="white")

# Generate artwork
base_box_size = 19.0
base_margin = 0.5
num_boxes_x = int(canvas.plottable_size[0] / (base_box_size + base_margin))    
num_boxes_y = int(canvas.plottable_size[1] / (base_box_size + base_margin))
base_box_size_x = (num_boxes_x * base_box_size + (num_boxes_x - 1) * base_margin) / num_boxes_x
base_box_size_y = (num_boxes_y * base_box_size + (num_boxes_y - 1) * base_margin) / num_boxes_y

# Calculate canvas center and edges
center_x = (canvas.bottom_right[0] + canvas.top_left[0]) / 2
center_y = (canvas.bottom_right[1] + canvas.top_left[1]) / 2
canvas_width = canvas.bottom_right[0] - canvas.top_left[0]
canvas_height = canvas.bottom_right[1] - canvas.top_left[1]

# Initial translation (previously done with canvas.translate(2,0))
offset_x = -2
chance_of_skip = 0.25
chance_of_skip_increase = 0.002
chance_of_fill = 1.0
chance_of_fill_increase = 0.03
chance_of_horizonal = 0.95
box_y_sub = 0
total_y_sub = 0

y_count = 0
canvas.push()
canvas.translate(-2,0)
for y in np.arange(canvas.top, canvas.bottom + 1000, base_box_size_y):
    box_x_sub = 0
    total_x_sub = 0
    x_count = 0
    for x in np.arange(canvas.left, canvas.right + 500, base_box_size_x):
        is_outline = (x_count + y_count + 1) % 2 == 0
        canvas.box(
            x - total_x_sub , 
            y - total_y_sub, 
            base_box_size - box_x_sub, 
            base_box_size - box_y_sub, 
            color="#ffffff",
            thickness=0.25,
            align_fill_to_edges=True,
            outline=False,
            fill_direction="vertical" if is_outline else "horizontal",
            fill_density=0.2 if is_outline else 0.15,
            filled=True)
        
        if x > canvas.width / 2 + 20:
            box_x_sub -= 1.5
            total_x_sub += box_x_sub + 1
        else:
            box_x_sub += 1.5
            total_x_sub += box_x_sub - 2
        if x + base_box_size_x > canvas.width + 50:
            break
        x_count += 1    
    if y > canvas.height / 2 + 20:
        box_y_sub -= 1.7
        total_y_sub += box_y_sub + 1
    else:
        box_y_sub += 1.7
        total_y_sub += box_y_sub - 2
    if y + base_box_size_y > canvas.height + 90:
        break
    y_count += 1
canvas.pop()

# Add signature
print("Drawing signature")
svg = SVG("signature25.svg")
svg.draw(canvas, canvas.canvas_size_mm[0] - canvas.margin - 40, canvas.canvas_size_mm[1] - canvas.margin+4, scale=1.5)

svg_text = SVGFont("alphabet.svg")
svg_text.draw(canvas, canvas.margin+72, 5, "GENUARY 09".upper(), scale=0.8, stroke_color="#ffffff", fill_color="#ffffff")

# Render preview
render = Render(canvas)
render.render()
render.show()

svg.save(canvas, "genuary_09.svg")

# Generate GCode
gcode = GCode(canvas)
gcode.generate()
gcode.save("sedov_genuary_09.gcode")