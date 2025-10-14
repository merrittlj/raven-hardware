import timeit
import math
from build123d import *
from build123d import extrude as _extrude

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

# thickness: battery + usb + pcb + epd + bezel
battery_thickness = 3
pcb_thickness = 1.6
epd_thickness = 1.05
# eg. total wall height
thickness = battery_thickness + usb_height + pcb_thickness + epd_thickness + bezel_thickness

# for the nato strap "holder"
# ideally ~20mm lug width
# 26 mm strap length(?)
lug_width = 18

holder_width = width - 8 
holder_height = thickness * 0.4
holder_inside_width = lug_width + 0.2 
holder_inside_outside = 2
holder_inside_base = 3
holder_base = holder_inside_base + holder_inside_outside
holder_drop = 3

assert holder_inside_width < holder_width
assert holder_width < width
assert holder_inside_base < holder_base

component_level = bezel_thickness + epd_thickness + pcb_thickness

# from outside of bezel to case edge
wall_thickness = 1.2

print(f"lug to lug: {height + wall_thickness * 2 + holder_base * 2}")
print(f"thickness: {thickness}")
print(f"width: {width + wall_thickness * 2}")
print(f"height: {height + wall_thickness * 2}")

def wall_hole(walls, side, hole_width, hole_height, center_offset, level):
    f = {
        "left": lambda: walls.faces().sort_by(Axis.X)[0],
        "right": lambda: walls.faces().sort_by(Axis.X)[-1],
    }[side]()
    be = f.edges().sort_by(Axis.Z)[0]
    p = Plane(be @ 0.5, x_dir=be.tangent_at(0.5), z_dir=f.normal_at())
    hole_align = (Align.CENTER, Align.MAX) if side == "left" else (Align.CENTER, Align.MIN)
    y_offset = -level + hole_height_padding if side == "left" else level - hole_height_padding
    hole = Rectangle(hole_width + hole_width_padding * 2, hole_height + hole_height_padding * 2, align=hole_align)
    return extrude(p * Pos(center_offset, y_offset, 0) * hole, -wall_thickness)

def extrude(shape, dir, center=False):
    if center:
        return _extrude(shape, dir/2) + _extrude(shape, -dir/2)
    else:
        return _extrude(shape, dir)

def holder(walls, side):
    f = {
        "top": lambda: walls.faces().filter_by(Axis.Y).sort_by(Axis.Y)[-1],
        "bottom": lambda: walls.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0],
    }[side]()
    e = f.edges().filter_by(GeomType.LINE).sort_by(Axis.Y)[-1]
    
    x_dir = f.normal_at()
    desired_y = Vector(0, 0, -1)
    crossed_z = x_dir.cross(desired_y)
    
    holder_plane = Plane(e @ 0.5, x_dir=x_dir, z_dir=crossed_z) * Pos(Y=-holder_drop)
    holder_plane_x = Axis(origin=(0, 0, 0), direction=holder_plane.x_dir)
    holder_shape = holder_plane * Polygon(*[(0, 0), (holder_base, -holder_drop), (0, holder_height)], align=(Align.MIN, Align.MIN))
    tip = holder_shape.vertices().sort_by(holder_plane_x)[-1]
    holder_shape = fillet(tip, radius=.25)
    holder = extrude(holder_shape, holder_width, center=True)

    holder_shape_flat = holder_plane * Polygon(*[(0, 0), (holder_base, 0), (0, holder_height)], align=(Align.MIN, Align.MIN))
    holder_flat = extrude(holder_shape_flat, holder_width, center=True)

    ff = holder_flat.faces().filter_by(Axis.Z)[-1]
    fe = ff.edges().sort_by(holder_plane_x)[-1]
    holder_inside_shape = Plane(fe @ 0.5, x_dir=Plane(ff).x_dir, z_dir=Plane(ff).z_dir) * Pos(X=-holder_inside_outside) * Rectangle(holder_inside_base, holder_inside_width, align=(Align.MAX, Align.CENTER))
    holder -= extrude(holder_inside_shape, -holder_height*2)

    return holder

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

walls = extrude(walls_shape, thickness)

walls -= wall_hole(walls, "left", usb_width, usb_height, usb_center_offset, component_level)

walls -= wall_hole(walls, "left", button_width, button_height, button_center_offset, component_level)
walls -= wall_hole(walls, "right", button_width, button_height, button_center_offset, component_level)
walls -= wall_hole(walls, "left", button_width, button_height, -button_center_offset, component_level)
walls -= wall_hole(walls, "right", button_width, button_height, -button_center_offset, component_level)

walls -= wall_hole(walls, "right", power_width, power_height, power_center_offset, component_level)

top_holder = holder(walls, "top")
bottom_holder = holder(walls, "bottom")
holders = Compound(top_holder + bottom_holder)

model = bezel + walls + holders
export_stl(model, "build.stl")
