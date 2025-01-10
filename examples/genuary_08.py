import os
import math, random
import numpy as np
os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from penpal.generators.points import PointGrid, AddPointTool
from penpal.operators.color import ApplyColor
from penpal.operators.offset import Offset
from penpal.utils import Optimizations
from penpal import Canvas, Render, SVG, GCode, SVGFont
from penpal.operators import DifferentialGrowth, Noise

# ---------------------------------------------------------------------------------
# 1) Set up the canvas, as in your snippet:
# ---------------------------------------------------------------------------------

canvas = Canvas(
    canvas_size_mm=(229.0, 305.0),
    paper_color="black",
    pen_color="white",
    respect_margin=True
)
render = Render(canvas)

# This is to illustrate the margin concept.  If respect_margin=True, then:
#   canvas.left, canvas.top, canvas.right, canvas.bottom
# will give you the "printable" area inside the margin. So,
#   top_left = (canvas.left, canvas.top)
#   bottom_right = (canvas.right, canvas.bottom)
#
# Or if you want to override margin, set canvas.respect_margin = False
# and use (0, 0) ... (canvas.canvas_size_mm[0], canvas.canvas_size_mm[1]).

# Let's define the actual starting point at the top-left corner *inside* the margin.
start_x = canvas.left
start_y = canvas.top

# ---------------------------------------------------------------------------------
# 2) Draw a single line that accumulates to exactly 1,000,000 mm length.
# ---------------------------------------------------------------------------------

total_length_needed = 1000000.0  # 1 million mm
accumulated_length = 0.0

# Choose a step size in mm. Smaller step => more detail, bigger step => less detail.
step_size = 1.0

# Direction in degrees. 0 means facing right (east). 
# We start angled “east” so that the first 90° or 30° turn will deviate from that.
direction = 0.0  

current_x = start_x
current_y = start_y

in_current_iter = 0
break_every = 50000
starting_color = "#ffffff"
# We'll keep going until we've drawn 1,000,000 mm total.
while accumulated_length < total_length_needed:

    if in_current_iter > break_every:
        # Change color every 100,000 mm
        # create a new random color
        starting_color = "#" + ''.join(random.choices('0123456789ABCDEF', k=6))
        in_current_iter = 0
        current_x = np.random.random() * (canvas.right - canvas.left) + canvas.left
        current_y = np.random.random() * (canvas.bottom - canvas.top) + canvas.top
    # If we have fewer than step_size mm left to reach 1,000,000,
    # just do a partial step for the final segment:
    this_step = min(step_size, total_length_needed - accumulated_length)
    
    # Randomly pick the angle (30 or 90).
    turn_angle = random.choice([30, 90])
    direction = (direction + turn_angle) % 360

    # Calculate next point
    next_x = current_x + this_step * math.cos(math.radians(direction))
    next_y = current_y + this_step * math.sin(math.radians(direction))
    
    # Check if next point is within the printable area
    # (canvas.left, canvas.right, canvas.top, canvas.bottom).
    #
    # If it is *outside*, let's bounce by inverting direction by 180°,
    # and skip the rest of this loop iteration. We'll just recalculate
    # in the next iteration with the new direction.
    if (next_x < canvas.left or next_x > canvas.right or
        next_y < canvas.top  or next_y > canvas.bottom):
        # Bounce: turn around 180°
        direction = (direction + 180) % 360
        continue
    
    # Draw the line
    canvas.line(current_x, current_y, next_x, next_y, color=starting_color, thickness=0.15)
    
    # Update total length, position
    accumulated_length += this_step
    in_current_iter+= this_step
    current_x, current_y = next_x, next_y

# ---------------------------------------------------------------------------------
# 3) (Optional) Draw anything else you want, then render.
# ---------------------------------------------------------------------------------

canvas.clear("points")
canvas.respect_margin = False

svg = SVG("signature25.svg")
svg.draw(canvas,
         canvas.canvas_size_mm[0] - canvas.margin - 48,
         canvas.canvas_size_mm[1] - canvas.margin + 4,
         scale=1.5)

svg_text = SVGFont("alphabet.svg")
svg_text.draw(canvas,
              canvas.margin + 72,
              5,
              "GENUARY 08".upper(),
              scale=0.8,
              stroke_color=None,
              fill_color="#ffffff")

render.render()
render.show()

gcode = GCode(canvas, move_speed=10000, draw_speed=1000)
gcode.generate()
gcode.save("sedov_genuary_08.gcode")