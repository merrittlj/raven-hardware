from solid2 import *
from solid2.extensions.bosl2 import rect

# set_global_fa(10)
# set_global_fs(0.2)

## units are mm!

# note: epd mechanical drawing specifies +-0.1mm for width/height
pcb_width = 31.8
pcb_height = 37.32

side_padding = 0.55
width = pcb_width + 2 * side_padding
height = pcb_height + 2 * side_padding

# measurements from display mechanical drawing
bezel_padding = 0.5
bezel_top = 2.40 - bezel_padding
bezel_left = 2.40 - bezel_padding
bezel_right = 2.40 - bezel_padding
bezel_bottom = 37.32 - 27 - 2.40 - bezel_padding # 7.92
# from case top downwards
bezel_thickness = 1.2

# holes are padding bigger than width/height, centered
# hole_width_padding = 0.25;
# hole_height_padding = 0.25;
hole_width_padding = 0;
hole_height_padding = 0;

# from product drawings
usb_width = 8.94;
# eg. usb thickness
usb_height = 3.31;
# from pcb, center y is 112.41
usb_center_offset = -3.6625;

# full button width: 4.7, plunger width: 2.6
button_width = 2.6;
button_height = 1.65;
button_top_center_offset = 17.26;
button_bottom_center_offset = -11.9615;

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

def wall_3d(shape_2d, thickness, height, radius=0):
    if radius > 0:
        outer = shape_2d.offset(r=radius).offset(delta=thickness - radius)
    else:
        outer = shape_2d.offset(delta=thickness)

    wall_2d = outer - shape_2d
    return wall_2d.linear_extrude(height, center=False)

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
    hole = cube([wall_thickness + 0.01, hole_width + hole_width_padding * 2, hole_height + hole_height_padding * 2], center=True)

    # Position base
    x, y, z = 0, 0, level + hole_height / 2

    if side == "left":
        x = -width / 2 - wall_thickness / 2
        y = offset_from_center
    elif side == "right":
        x = width / 2 + wall_thickness / 2
        y = offset_from_center
    elif side == "top":
        hole = cube([hole_width, wall_thickness + 0.01, hole_height], center=True)
        x = offset_from_center
        y = height / 2 + wall_thickness / 2
    elif side == "bottom":
        hole = cube([hole_width, wall_thickness + 0.01, hole_height], center=True)
        x = offset_from_center
        y = -height / 2 - wall_thickness / 2
    else:
        raise ValueError("side must be one of: 'left', 'right', 'top', 'bottom'")

    hole = hole.translate([x, y, z])
    return wall_shape - hole

# Inside shape - walls are added on the outside of this shape
base_shape = rect([width, height])
bezel_inner = rect([
    pcb_width - bezel_left - bezel_right,
    pcb_height - bezel_top - bezel_bottom
    ]).offset(r=0.5, delta=0).translate([0, -(bezel_top + bezel_bottom)/2.0 + bezel_bottom])
bezel = base_shape - bezel_inner
bezel = bezel.linear_extrude(bezel_thickness, center=False)

wall = wall_3d(base_shape, wall_thickness, thickness, 5);

wall = add_wall_hole(wall, usb_height, usb_width, usb_center_offset, "left", component_level)

wall = add_wall_hole(wall, button_height, button_width, button_top_center_offset, "left", component_level)
wall = add_wall_hole(wall, button_height, button_width, button_top_center_offset, "right", component_level)
wall = add_wall_hole(wall, button_height, button_width, button_bottom_center_offset, "left", component_level)
wall = add_wall_hole(wall, button_height, button_width, button_bottom_center_offset, "right", component_level)

model = bezel + wall
model.save_as_scad()
