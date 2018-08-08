bl_info = {
    "name": "New Toy Brick",
    "author": "Liam Owen",
    "version": (1, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Add > Mesh > New Brick",
    "description": "Adds a new Toy Brick Mesh",
    "warning": "",
    "wiki_url": "",
    "category": "Add Mesh",
    }

import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty, IntVectorProperty, BoolProperty, IntProperty, FloatProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector
from math import sin, cos, tan, radians, isclose
from enum import Enum

h_unit_size = 0.8
v_unit_size = 0.96
wall_thickness = 0.16
stud_outer_radius = 0.24
stud_inner_radius = 0
stud_segments = 12
stud_height = 0.16
tube_outer_radius = 0.3256
tube_inner_radius = 0.24
tube_segments = 12

def add_object(self, context):
    scale_x = self.scale[0]
    scale_y = self.scale[1]
    scale_z = self.scale[2]

    scale_x *= self.h_unit_size
    scale_y *= self.h_unit_size
    scale_z *= self.v_unit_size

    verts = [
             # 0, 1, 2, 3 - Bottom Bounds
             Vector((-0.5 * scale_x, 0.5 * scale_y, 0)),
             Vector((0.5 * scale_x, 0.5 * scale_y, 0)),
             Vector((0.5 * scale_x, -0.5 * scale_y, 0)),
             Vector((-0.5 * scale_x, -0.5 * scale_y, 0)),
             # 4, 5, 6, 7 - Top Bounds
             Vector((-0.5 * scale_x, 0.5 * scale_y, 1 * scale_z)),
             Vector((0.5 * scale_x, 0.5 * scale_y, 1 * scale_z)),
             Vector((0.5 * scale_x, -0.5 * scale_y, 1 * scale_z)),
             Vector((-0.5 * scale_x, -0.5 * scale_y, 1 * scale_z)),
             # 8, 9, 10, 11 - Inside Bottom Wall
             Vector(((-0.5 * scale_x) + self.wall_width, (0.5 * scale_y) - self.wall_width , 0)),
             Vector(((0.5 * scale_x) - self.wall_width, (0.5 * scale_y) - self.wall_width , 0)),
             Vector(((0.5 * scale_x) - self.wall_width, (-0.5 * scale_y) + self.wall_width, 0)),
             Vector(((-0.5 * scale_x) + self.wall_width, (-0.5 * scale_y) + self.wall_width, 0)),
             # 12, 13, 14, 15 - Inside Top Wall
             Vector(((-0.5 * scale_x) + self.wall_width, (0.5 * scale_y) - self.wall_width , 1 * scale_z - self.wall_width)),
             Vector(((0.5 * scale_x) - self.wall_width, (0.5 * scale_y) - self.wall_width , 1 * scale_z - self.wall_width)),
             Vector(((0.5 * scale_x) - self.wall_width, (-0.5 * scale_y) + self.wall_width, 1 * scale_z - self.wall_width)),
             Vector(((-0.5 * scale_x) + self.wall_width, (-0.5 * scale_y) + self.wall_width, 1 * scale_z - self.wall_width)),
            ]

    edges = []

    faces = [
             # Top
             [4, 7, 6, 5],
             # Sides
             [0, 4, 5, 1], [3, 7, 4, 0], [2, 6, 7, 3], [1, 5, 6, 2],
             # Bottom Wall
             [2, 3, 11, 10], [0, 8, 11, 3], [0, 1, 9, 8], [1, 2, 10, 9],
             # Top Wall
             [12, 13, 14, 15],
             # Inside Walls
             [10, 11, 15, 14], [9, 10, 14, 13], [8, 9, 13, 12], [8, 12, 15, 11],
            ]

    # Add studs
    stud_origins = get_origins(self.h_unit_size, self.scale[0], self.scale[1], scale_z)
    studs = generate_cylinders(stud_origins, self.stud_segments, self.stud_outer_radius, self.stud_inner_radius, self.stud_height, len(verts), False, True)
    verts.extend(studs.verts)
    faces.extend(studs.faces)
    
    # Add tubes
    tube_origins = get_origins(self.h_unit_size, self.scale[0] - 1, self.scale[1] - 1, 0)
    tubes = generate_cylinders(tube_origins, self.tube_segments, self.tube_outer_radius, self.tube_inner_radius, scale_z - self.wall_width, len(verts), True, False)
    verts.extend(tubes.verts)
    faces.extend(tubes.faces)

    mesh = bpy.data.meshes.new(name="New Toy Brick")
    mesh.from_pydata(verts, edges, faces)
    # useful for development when the mesh may be invalid.
    # mesh.validate(verbose=True)
    object_data_add(context, mesh, operator=self)
    mesh.use_auto_smooth = 1
    mesh.auto_smooth_angle = radians(80)
    bpy.ops.object.shade_smooth()

# class CapType(Enum):
#     NONE = 1
#     NGON = 2
#     FAN = 3

class MeshInfo(object):
    """docstring for MeshInfo"""
    def __init__(self, verts, faces):
        self.verts = verts
        self.faces = faces     

class OBJECT_OT_add_object(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_object"
    bl_label = "Add Mesh Object"
    bl_options = {'REGISTER', 'UNDO'}

    scale         = IntVectorProperty(
                    name="Scale",
                    default=(2.0, 4.0, 1.0),
                    soft_min=1,
                    description="scaling",
                    )

    h_unit_size   = FloatProperty(
                    name="Horizontal Unit Size",
                    default= 0.8,
                    soft_min=0.01,
                    description="scaling",
                    )
    v_unit_size   = FloatProperty(
                    name="Vertical Unit Size",
                    default= 0.96,
                    soft_min=0.01,
                    description="scaling",
                    )
    wall_width    = FloatProperty(
                    name="Wall Width",
                    default= 0.16,
                    soft_min=0.01,
                    description="scaling",
                    )
    stud_outer_radius   = FloatProperty(
                    name="Stud Outer Radius",
                    default= 0.24,
                    soft_min=0.01,
                    description="scaling",
                    )
    stud_inner_radius   = FloatProperty(
                    name="Stud Inner Radius",
                    default= 0,
                    soft_min=0,
                    description="scaling",
                    )
    stud_segments   = IntProperty(
                    name="Stud Segments",
                    default= 12,
                    soft_min=0,
                    description="scaling",
                    )
    stud_height   = FloatProperty(
                    name="Stud Height",
                    default= 0.16,
                    soft_min=0,
                    description="scaling",
                    )
    tube_outer_radius   = FloatProperty(
                    name="Tube Outer Radius",
                    default= 0.3256,
                    soft_min=0.01,
                    description="scaling",
                    )
    tube_inner_radius   = FloatProperty(
                    name="Tube Inner Radius",
                    default= 0.24,
                    soft_min=0,
                    description="scaling",
                    )
    tube_segments   = IntProperty(
                    name="Tube Segments",
                    default= 12,
                    soft_min=0,
                    description="scaling",
                    )


    def execute(self, context):

        add_object(self, context)

        return {'FINISHED'}

def get_origins(distance, x_count, y_count, z_pos):
    result = []
    offset = Vector (((x_count - 1) * distance / 2, (y_count - 1) * distance / 2, 0))
    for x in range(0, x_count):
        for y in range(0, y_count):
            origin = Vector((x * distance, y * distance, z_pos)) - offset
            result.append(origin)
    return result

def generate_cylinder_verts(origin, segments, outer_radius, inner_radius, height):
    result = []
    is_hollow = inner_radius != 0
    for i in range(0, segments):
        angle = radians((360 / segments) * i)
        btm_out = Vector((sin(angle) * outer_radius, cos(angle) * outer_radius, 0))
        top_out = btm_out + Vector((0, 0, height))
        result.append(btm_out + origin)
        result.append(top_out + origin)
        if (is_hollow):
            btm_in  = Vector((sin(angle) * inner_radius, cos(angle) * inner_radius, 0))
            top_in  = btm_in + Vector((0, 0, height))
            result.append(btm_in + origin)
            result.append(top_in + origin)
    return result

def connect_cylinder_verts(segments, length, bottom_cap, top_cap, is_hollow):
    result = []
    increment = 4 if is_hollow else 2
    vert_count = segments * increment
    r_start = length - vert_count
    for j in range (r_start, length, increment):

        if is_hollow:
            result.append([
                j,
                (j - r_start + 1) % vert_count + r_start,
                (j - r_start + 5) % vert_count + r_start,
                (j - r_start + 4) % vert_count + r_start
            ])
            result.append([
                (j - r_start + 6) % vert_count + r_start,
                (j - r_start + 7) % vert_count + r_start,
                (j - r_start + 3) % vert_count + r_start,
                (j - r_start + 2) % vert_count + r_start
            ])
            if (bottom_cap):
                result.append([
                    (j - r_start + 4) % vert_count + r_start,
                    (j - r_start + 6) % vert_count + r_start,
                    (j - r_start + 2) % vert_count + r_start,
                    (j - r_start + 0) % vert_count + r_start
                ])
            if (top_cap):
                result.append([
                    (j - r_start + 1) % vert_count + r_start,
                    (j - r_start + 3) % vert_count + r_start,
                    (j - r_start + 7) % vert_count + r_start,
                    (j - r_start + 5) % vert_count + r_start
                ])
        else:
            result.append([
                j,
                (j - r_start + 1) % vert_count + r_start,
                (j - r_start + 3) % vert_count + r_start,
                (j - r_start + 2) % vert_count + r_start
            ])
            if (bottom_cap):
                result.append([
                    j,
                    (j - r_start + 2) % vert_count + r_start,
                    r_start - 1 - int(top_cap)
                ])
            if (top_cap):
                result.append([
                    (j - r_start + 3) % vert_count + r_start,
                    (j - r_start + 1) % vert_count + r_start,
                    r_start - 1
                ])

    return result

def generate_cylinders(origins, segments, outer_radius, inner_radius, height, verts_array_length, bottom_cap, top_cap):
    verts = []
    faces = []
    is_hollow = inner_radius != 0
    print(is_hollow)
    for i in range(0, len(origins)):
        if (not is_hollow):
            if (bottom_cap):
                verts.append(origins[i])
            if (top_cap):
                verts.append(origins[i] + Vector((0, 0, height)))
        verts.extend(generate_cylinder_verts(origins[i], segments, outer_radius, inner_radius, height))
        faces.extend(connect_cylinder_verts(segments, verts_array_length + len(verts), bottom_cap, top_cap, is_hollow))
    # print_collection(verts)
    return MeshInfo(verts, faces)

def print_collection(col):
    for i in range(0, len(col)):
        print (str(i) + " = " + str(col[i]))

# Registration

def add_object_button(self, context):
    self.layout.operator(
        OBJECT_OT_add_object.bl_idname,
        text="Add Toy Brick",
        icon='MOD_BUILD')

# This allows you to right click on a button and link to the manual
def add_object_manual_map():
    url_manual_prefix = "https://docs.blender.org/manual/en/dev/"
    url_manual_mapping = (
        ("bpy.ops.mesh.add_object", "editors/3dview/object"),
        )
    return url_manual_prefix, url_manual_mapping

def register():
    bpy.utils.register_class(OBJECT_OT_add_object)
    bpy.utils.register_manual_map(add_object_manual_map)
    bpy.types.INFO_MT_mesh_add.append(add_object_button)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_object)
    bpy.utils.unregister_manual_map(add_object_manual_map)
    bpy.types.INFO_MT_mesh_add.remove(add_object_button)

if __name__ == "__main__":
    register()
