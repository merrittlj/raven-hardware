from build123d import *

# note: epd mechanical drawing specifies +-0.1mm for width/height
pcb_width = 31.80
pcb_height = 37.32

side_padding = 0.80
bottom_side_padding = 2
width = pcb_width + 2 * side_padding
height = pcb_height + 2 * side_padding + bottom_side_padding

# measurements from display mechanical drawing
bezel_top = 2.40 - 0.5
bezel_left = 2.40 - 0.55
bezel_right = 2.40 - 0.55
bezel_bottom = 37.32 - 27 - 2.40 - 0.45
# from case top downwards
bezel_thickness = 1.2

# add extra space around holes
hole_width_padding = 1
hole_height_padding = 1

# from product drawings
usb_width = 8.94
# eg. usb thickness
usb_height = 3.31
# from pcb, center y is 112.41
usb_center_offset = -3.6625

# full button width: 4.7, plunger width: 2.6
button_width = 3
button_height = 1.65
button_top_center_offset = 14.63
button_bottom_center_offset = -14.59

power_width = 2.6
# 1.4 +- 0.2
power_height = 1.6
power_center_offset = -3.663

# for the strap "holder"
# ideally for ~20-21mm nato strap
holder_width = width - 4 
holder_base = 6
holder_height = 5
holder_inside_base = holder_base - 3
holder_inside_width = holder_width - 6 
holder_inside_height = holder_height + 6 

# thickness: battery + usb + pcb + epd + bezel
battery_thickness = 3
pcb_thickness = 1.6
epd_thickness = 1.05
# eg. total wall height
thickness = battery_thickness + usb_height + pcb_thickness + epd_thickness + bezel_thickness

component_level = bezel_thickness + epd_thickness + pcb_thickness

# from outside of bezel to case edge
wall_thickness = 1.2

# Inside shape - walls are added on the outside of this shape
# base_shape = rect([width, height]).translateY(-bottom_side_padding / 2)
# bezel_inner = rect([
    # pcb_width - bezel_left - bezel_right,
    # pcb_height - bezel_top - bezel_bottom
    # ], rounding=2).translateY(-(bezel_top + bezel_bottom)/2.0 + bezel_bottom)
# bezel = base_shape - bezel_inner
# bezel = bezel.linear_extrude(bezel_thickness, center=False)

base = Rectangle(width, height)
bezel_inner = Rectangle(
    pcb_width - bezel_left - bezel_right,
    pcb_height - bezel_top - bezel_bottom
)
tope = base.edges().filter_by(GeomType.LINE).filter_by(Axis.Y)
bezel = base - (Plane(tope) * Pos(Y=-bezel_top) * bezel_inner)
bezel = extrude(bezel, amount=bezel_thickness)

export_stl(bezel, "build.stl")
