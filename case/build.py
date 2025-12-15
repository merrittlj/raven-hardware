import timeit
import math
from build123d import *
from build123d import extrude as _extrude

start_time = timeit.default_timer()

# note: epd mechanical drawing specifies +-0.1mm for width/height
pcb_width = 31.80
pcb_height = 37.32

button_cap_inside = 1

lr_padding = 0.5 + button_cap_inside
tb_padding = 0.2
width = pcb_width + 2 * lr_padding
height = pcb_height + 2 * tb_padding

# measurements from display mechanical drawing
bezel_top = 2.40 - 1.2
bezel_left = 2.40 - 1.3
bezel_right = 2.40 - 1.3
bezel_bottom = 37.32 - 27 - 2.40 - 1.3
# from case top downwards
bezel_thickness = 1.2

# add extra space around holes
hole_width_padding = 1
hole_height_padding = 1

usb_extra_hole_width_padding = 1
usb_extra_hole_height_padding = 1
power_extra_hole_width_padding = 1.5
power_extra_hole_height_padding = 1.5

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
# ideally ~18mm lug width
# 26 mm strap length(?)
lug_width = 18

holder_width = width - 8 
holder_height = thickness * 0.4
holder_inside_width = lug_width + 0.2 
holder_inside_outside = 3
holder_inside_base = 3
holder_base = holder_inside_base + holder_inside_outside
holder_drop = 3

assert holder_inside_width < holder_width
assert holder_width < width
assert holder_inside_base < holder_base

component_level = bezel_thickness + epd_thickness + pcb_thickness

# from outside of bezel to case edge
wall_thickness = 1.75

catch_extra_width = 0.75
catch_extra_height = 0.75

button_cap_reach = 3
button_cap_clearance = 0.5

# power_cap_inside = 1
# power_cap_reach = 1
# power_cap_clearance = 0.1

bottom_thickness = 1
bottom_inside_thickness = 0.7
bottom_reduce = 0.2

print(f"lug to lug: {height + wall_thickness * 2 + holder_base * 2}")
print(f"thickness: {thickness + bottom_thickness}")
print(f"width: {width + wall_thickness * 2}")
print(f"height: {height + wall_thickness * 2}")
print(f"space bezel->component: {component_level - bezel_thickness}")

assert catch_extra_height < component_level - bezel_thickness

def topf(obj):
    return obj.faces().sort_by(Axis.Z)[-1]

def wall_hole(walls, side, hole_width, hole_height, center_offset, level=component_level):
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

def button_cap(hole_width, hole_height, inside_thickness, outside_reach, hole_clearance):
    real_width = hole_width + hole_width_padding * 2
    real_height = hole_height + hole_height_padding * 2
    catch = extrude(Rectangle(real_width + catch_extra_width * 2, real_height + catch_extra_height * 2), inside_thickness)
    reach = Plane(topf(catch)) * extrude(Rectangle(real_width - hole_clearance, real_height - hole_clearance), outside_reach)
    return catch + reach

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
    holder_shape = fillet(tip, radius=0.5)
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
# rounded_base = fillet(base.vertices(), 3)
rounded_base = base
bezel_shape = rounded_base - fillet((Location(tope @ 0.5) * Pos(Y=-bezel_top) * bezel_inner).vertices(), 2)
bezel = extrude(bezel_shape, bezel_thickness)

walls_shape = offset(fillet(base.vertices(), 3), wall_thickness)
walls = extrude(walls_shape - base, thickness)
# walls = fillet(walls.edges().filter_by(Axis.Z), 3)

walls -= wall_hole(walls, "left", usb_width + usb_extra_hole_width_padding, usb_height + usb_extra_hole_height_padding, usb_center_offset)

walls -= wall_hole(walls, "left", button_width, button_height, button_center_offset)
walls -= wall_hole(walls, "right", button_width, button_height, button_center_offset)
walls -= wall_hole(walls, "left", button_width, button_height, -button_center_offset)
walls -= wall_hole(walls, "right", button_width, button_height, -button_center_offset)

walls -= wall_hole(walls, "right", power_width + power_extra_hole_width_padding, power_height + power_extra_hole_height_padding, power_center_offset)

re = Plane(walls_shape.edges().sort_by(Axis.X)[-1] @ 0.5)

caps = Compound([
    loc * button_cap(button_width, button_height, button_cap_inside, button_cap_reach, button_cap_clearance)
    for loc in GridLocations(20, 20, 2, 2)
])
# caps += Pos(Y=button_height * 8) * button_cap(power_width, power_height, power_cap_inside, power_cap_reach, power_cap_clearance)
caps = re * Pos(X=30) * caps

bottom_base = extrude(walls_shape, bottom_thickness)
inside = Plane(topf(bottom_base)) * extrude(offset(rounded_base, -bottom_reduce), bottom_inside_thickness)
bottom = Compound([re * Pos(X=75) * (bottom_base + inside)])

top_holder = holder(walls, "top")
bottom_holder = holder(walls, "bottom")
holders = Compound(top_holder + bottom_holder)

model = Compound(bezel + walls + holders + caps + bottom)
# model = (bezel + walls + holders)
export_stl(model, "build.stl")
