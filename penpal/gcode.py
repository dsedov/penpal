class GCode:
    def __init__(self, canvas):
        self.canvas = canvas
        self.state_x = 0
        self.state_y = 0
        self.state_z = 1.0
        self.precision = 0.01
        self.draw_speed = 8000
        self.move_speed = 30000
        self.gcode = []
        self.verbose = True
        self.pen_up_z = 1.0
        self.pen_down_z = 0.0

        self.gcode.append("G21 ; Set units to millimeters")
        self.gcode.append("G90 ; Use absolute positioning")    
        # Move pen up
        self.gcode.append(f"G0 Z{self.pen_up_z}")
        self._dwell()


    def generate(self):
        grouped_by_color = {}
        for op in self.canvas.draw_stack:
            if op["type"] == "line":
                if op["color"] not in grouped_by_color:
                    grouped_by_color[op["color"]] = []
                grouped_by_color[op["color"]].append(op)
        
        for color in grouped_by_color:
            print(f"Color: {color}")

            for op in grouped_by_color[color]:
                if op["type"] == "line":
                    line_start_x = op["x1"]
                    line_start_y = op["y1"]
                    line_end_x = op["x2"]
                    line_end_y = op["y2"]

                    if self.verbose:
                        self.gcode.append(f"; Line from {line_start_x}, {line_start_y} to {line_end_x}, {line_end_y}")

                    if self._is_close_to(line_start_x, line_start_y, self.state_z):
                        self.gcode.append(f"G1 X{line_end_x} Y{line_end_y} F{self.draw_speed}")
                        self.state_x = line_end_x
                        self.state_y = line_end_y
                    else:
                        self.gcode.append(f"G0 Z{self.pen_up_z}")
                        self.state_z = self.pen_up_z
                        self._dwell()

                        self.gcode.append(f"G0 X{line_start_x} Y{line_start_y} F{self.move_speed}")
                        self.state_x = line_start_x
                        self.state_y = line_start_y

                        self.gcode.append(f"G0 Z{self.pen_down_z}")
                        self.state_z = self.pen_down_z
                        self._dwell()
                     
                        self.gcode.append(f"G1 X{line_end_x} Y{line_end_y} F{self.draw_speed}")
                        self.state_x = line_end_x
                        self.state_y = line_end_y
    def save(self, filename):          
        with open(filename, "w") as f:
            for line in self.gcode:
                f.write(line + "\n")
                
    def _is_close_to(self, x, y, z=None):
        if z is None:
            return abs(self.state_x - x) < self.precision and abs(self.state_y - y) < self.precision
        else:
            return abs(self.state_x - x) < self.precision and abs(self.state_y - y) < self.precision and abs(self.state_z - z) < self.precision
    
    def _dwell(self, time_s = 0.05):
        self.gcode.append(f"G4 P{time_s}")            
    