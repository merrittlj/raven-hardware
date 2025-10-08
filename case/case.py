from solid2 import *
from solid2.extensions.bosl2 import rect

# set_global_fa(10)
# set_global_fs(0.2)

## units are mm!

# note: epd mechanical drawing specifies +-0.1mm for width/height
pcb_width = 31.8
pcb_height = 37.32

# measurements from display mechanical drawing
bezel_top = 2.40
bezel_left = 2.40
bezel_right = 2.40
bezel_bottom = 37.32 - 27 - bezel_top # 7.92
# from case top downwards
bezel_thickness = 1.2

# thickness: battery + usb + pcb + epd + bezel
battery_thickness = 3
# from usb connector product drawings
usb_thickness = 3.31
pcb_thickness = 1.6
epd_thickness = 1.05

# eg. total wall height
thickness = battery_thickness + usb_thickness + pcb_thickness + epd_thickness + bezel_thickness

# from outside of bezel to case edge
wall_thickness = 1.2
# corner radius of the walls
corner_radius = 5

side_padding = 0.1
width = pcb_width + 2 * side_padding
height = pcb_height + 2 * side_padding

# def wall_3d(shape_2d, thickness, height):
    # wall_2d = shape_2d.offset(thickness) - shape_2d
    # return wall_2d.linear_extrude(height)
def wall_3d(shape_2d, thickness, height, radius=0):
    if radius > 0:
        outer = shape_2d.offset(r=corner_radius).offset(delta=thickness - radius)
    else:
        outer = shape_2d.offset(delta=thickness)

    wall_2d = outer - shape_2d
    return wall_2d.linear_extrude(height, center=False)

# Inside shape - walls are added on the outside of this shape
base_shape = rect([width, height])
bezel_inner = rect([
    pcb_width - bezel_left - bezel_right,
    pcb_height - bezel_top - bezel_bottom
]).translate([0, -(bezel_top + bezel_bottom)/2.0 + bezel_bottom])
bezel = base_shape - bezel_inner
bezel = bezel.linear_extrude(bezel_thickness, center=False)

wall = wall_3d(base_shape, wall_thickness, thickness, corner_radius);

model = bezel + wall
model.save_as_scad()
