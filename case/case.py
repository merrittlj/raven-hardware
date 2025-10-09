from solid2 import *
from solid2.extensions.bosl2 import *

# note: epd mechanical drawing specifies +-0.1mm for width/height
pcb_width = 31.8
pcb_height = 37.32

side_padding = 0.55 + 0.25
bottom_side_padding = 3
width = pcb_width + 2 * side_padding
height = pcb_height + 2 * side_padding + bottom_side_padding

# measurements from display mechanical drawing
bezel_padding = 0.5
bezel_padding_bottom = 0.35
bezel_top = 2.40 - bezel_padding
bezel_left = 2.40 - bezel_padding
bezel_right = 2.40 - bezel_padding
bezel_bottom = 37.32 - 27 - 2.40 - bezel_padding_bottom # 7.92
# from case top downwards
bezel_thickness = 1.2

# holes are padding bigger than width/height, centered
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
holder_width = width - 4 
holder_base = 6
holder_height = 5
holder_inside_base = holder_base - 3
holder_inside_width = holder_width - 6 
holder_inside_height = holder_height + 6 
holder_inside_extra = 3

# thickness: battery + usb + pcb + epd + bezel
battery_thickness = 3
pcb_thickness = 1.6
epd_thickness = 1.05
# eg. total wall height
thickness = battery_thickness + usb_height + pcb_thickness + epd_thickness + bezel_thickness

component_level = bezel_thickness + epd_thickness + pcb_thickness

# from outside of bezel to case edge
wall_thickness = 1.2
# corner radius of the walls

def add_wall_hole(
        wall_shape,
        hole_height,
        hole_width,
        offset_from_center,
        side,
        level,
        ):
    """
    Cut a rectangular hole into a specified wall side ("left", "right", "top", or "bottom").

    Args:
        wall_shape: The 3D wall solid to subtract from.
        hole_height: Vertical height of the hole (along Z axis).
        hole_width: Horizontal width of the hole opening.
        offset_from_center: Offset from the wall’s centerline (mm).
            - For "left"/"right": offset is along Y (up-down direction)
            - For "top"/"bottom": offset is along X (left-right direction)
        side: Which wall to cut ("left", "right", "top", "bottom").
        level: Z height from base where hole starts.
    """

    # Base cube for the hole (centered)
    hole_shape = rect([hole_width + hole_width_padding * 2, hole_height + hole_height_padding * 2], rounding=0.5)
    hole = hole_shape.linear_extrude(wall_thickness + 0.1, center=True)

    x, y, z = 0, 0, level + hole_height / 2

    if side == "left":
        x = -width / 2 - wall_thickness / 2
        y = offset_from_center
        hole = hole.rotateX(90)
        hole = hole.rotateZ(90)
    elif side == "right":
        x = width / 2 + wall_thickness / 2
        y = offset_from_center
        hole = hole.rotateX(90)
        hole = hole.rotateZ(90)
    elif side == "top":
        x = offset_from_center
        y = height / 2 + wall_thickness / 2
        hole = hole.rotateX(90)
    elif side == "bottom":
        x = offset_from_center
        y = -height / 2 - wall_thickness / 2
        hole = hole.rotateX(90)
    else:
        raise ValueError("side must be one of: 'left', 'right', 'top', 'bottom'")

    hole = hole.translate([x, y, z])
    return wall_shape - hole

# Inside shape - walls are added on the outside of this shape
base_shape = rect([width, height]).translateY(-bottom_side_padding / 2)
bezel_inner = rect([
    pcb_width - bezel_left - bezel_right,
    pcb_height - bezel_top - bezel_bottom
    ], rounding=2).translateY(-(bezel_top + bezel_bottom)/2.0 + bezel_bottom)
bezel = base_shape - bezel_inner
bezel = bezel.linear_extrude(bezel_thickness, center=False)

wall = shell2d(wall_thickness, 2, 2)(base_shape).linear_extrude(thickness, center=False)

wall = add_wall_hole(wall, usb_height, usb_width, usb_center_offset, "left", component_level)

wall = add_wall_hole(wall, button_height, button_width, button_top_center_offset, "left", component_level)
wall = add_wall_hole(wall, button_height, button_width, button_top_center_offset, "right", component_level)
wall = add_wall_hole(wall, button_height, button_width, button_bottom_center_offset, "left", component_level)
wall = add_wall_hole(wall, button_height, button_width, button_bottom_center_offset, "right", component_level)

wall = add_wall_hole(wall, power_height, power_width, power_center_offset, "right", component_level)

top_holder_shape = right_triangle([holder_base, holder_height], center=True)
top_holder_inside_shape = right_triangle([holder_inside_base, holder_inside_height], center=True).translateY(holder_inside_extra)
top_holder = top_holder_shape.linear_extrude(holder_width, center=True)
top_holder = top_holder - top_holder_inside_shape.linear_extrude(holder_inside_width, center=True)
top_holder = top_holder.rotate([-90, 0, 90]).translate([0, height / 2 + wall_thickness * 2, thickness - holder_height / 2])

bottom_holder_shape = right_triangle([holder_base, holder_height], center=True)
bottom_holder_inside_shape = right_triangle([holder_inside_base, holder_inside_height], center=True).translateY(holder_inside_extra)
bottom_holder = bottom_holder_shape.linear_extrude(holder_width, center=True)
bottom_holder = bottom_holder - bottom_holder_inside_shape.linear_extrude(holder_inside_width, center=True)
bottom_holder = bottom_holder.rotate([-90, 0, -90]).translate([0, -height / 2 - wall_thickness * 2 - bottom_side_padding, thickness - holder_height / 2])

holders = top_holder + bottom_holder

model = bezel + wall + holders
model.save_as_scad()
