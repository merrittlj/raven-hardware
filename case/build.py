import timeit
from build123d import *

start_time = timeit.default_timer()

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
button_center_offset = 14.63

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
holder_inside_outside = 2

# thickness: battery + usb + pcb + epd + bezel
battery_thickness = 3
pcb_thickness = 1.6
epd_thickness = 1.05
# eg. total wall height
thickness = battery_thickness + usb_height + pcb_thickness + epd_thickness + bezel_thickness

component_level = bezel_thickness + epd_thickness + pcb_thickness

# from outside of bezel to case edge
wall_thickness = 1.2

def wall_hole(wall, side, hole_width, hole_height, center_offset, level):
    f = {
        "left": lambda: wall.faces().sort_by(Axis.X)[0],
        "right": lambda: wall.faces().sort_by(Axis.X)[-1],
    }[side]()
    be = f.edges().sort_by(Axis.Z)[0]
    p = Plane(be @ 0.5, x_dir=be.tangent_at(0.5), z_dir=f.normal_at())
    hole_align = (Align.CENTER, Align.MAX) if side == "left" else (Align.CENTER, Align.MIN)
    y_offset = -level + hole_height_padding if side == "left" else level - hole_height_padding
    hole = Rectangle(hole_width + hole_width_padding * 2, hole_height + hole_height_padding * 2, align=hole_align)
    return extrude(p * Pos(center_offset, y_offset, 0) * hole, -wall_thickness)

base = Rectangle(width, height)
bezel_inner = Rectangle(
    pcb_width - bezel_left - bezel_right,
    pcb_height - bezel_top - bezel_bottom,
    align=(Align.CENTER, Align.MAX)
)
tope = base.edges().filter_by(GeomType.LINE).sort_by(Axis.Y)[-1]
bezel_shape = fillet(base.vertices(), 4)
walls_shape = offset(bezel_shape, wall_thickness) - bezel_shape
bezel_shape -= fillet((Location(tope @ 0.5) * Pos(Y=-bezel_top) * bezel_inner).vertices(), 2)
bezel = extrude(bezel_shape, bezel_thickness)

wall = extrude(walls_shape, thickness)

wall -= wall_hole(wall, "left", usb_width, usb_height, usb_center_offset, component_level)

wall -= wall_hole(wall, "left", button_width, button_height, button_center_offset, component_level)
wall -= wall_hole(wall, "right", button_width, button_height, button_center_offset, component_level)
wall -= wall_hole(wall, "left", button_width, button_height, -button_center_offset, component_level)
wall -= wall_hole(wall, "right", button_width, button_height, -button_center_offset, component_level)

wall -= wall_hole(wall, "right", power_width, power_height, power_center_offset, component_level)

# holder_shape = Polygon((0, 0), (holder_base, 0), (0, holder_height))
holder_shape = Triangle(a=holder_base, c=holder_height, B=90)
holder = extrude(holder_shape, holder_width)
bf = holder.faces().filter_by(Axis.Y)[0]
holder_inside_shape = Plane(bf) * Pos(X=-holder_inside_outside) * Rectangle(holder_inside_base, holder_inside_width, align=(Align.MIN, Align.CENTER))
holder -= extrude(holder_inside_shape, -holder_height)
topf = wall.faces().filter_by(Axis.Y).sort_by(Axis.Y)[-1]
holder = Plane(topf, z_dir=topf.normal_at()) * holder
# top_holder_shape = right_triangle([holder_base, holder_height], center=True)
# top_holder_inside_shape = right_triangle([holder_inside_base, holder_inside_height], center=True).translateY(holder_inside_extra)
# top_holder = top_holder_shape.linear_extrude(holder_width, center=True)
# top_holder = top_holder - top_holder_inside_shape.linear_extrude(holder_inside_width, center=True)
# top_holder = top_holder.rotate([-90, 0, 90]).translate([0, height / 2 + wall_thickness * 2, thickness - holder_height / 2])

# bottom_holder_shape = right_triangle([holder_base, holder_height], center=True)
# bottom_holder_inside_shape = right_triangle([holder_inside_base, holder_inside_height], center=True).translateY(holder_inside_extra)
# bottom_holder = bottom_holder_shape.linear_extrude(holder_width, center=True)
# bottom_holder = bottom_holder - bottom_holder_inside_shape.linear_extrude(holder_inside_width, center=True)
# bottom_holder = bottom_holder.rotate([-90, 0, -90]).translate([0, -height / 2 - wall_thickness * 2 - bottom_side_padding, thickness - holder_height / 2])

model = bezel + holder
export_stl(model, "build.stl")

print(f"Time: {timeit.default_timer() - start_time:0.3f}s")
