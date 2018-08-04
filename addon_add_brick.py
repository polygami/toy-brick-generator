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
from bpy.props import FloatVectorProperty, IntVectorProperty, BoolProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector
from math import sin, cos, tan, radians

h_unit_size = 0.8
v_unit_size = 0.96
wall_thickness = 0.16
stud_radius = 0.24
stud_segments = 12
stud_height = 0.16

def add_object(self, context):
    scale_x = self.scale[0]
    scale_y = self.scale[1]
    scale_z = self.scale[2]

    scale_x *= h_unit_size
    scale_y *= h_unit_size
    scale_z *= v_unit_size


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
             Vector(((-0.5 * scale_x) + wall_thickness, (0.5 * scale_y) - wall_thickness , 0)),
             Vector(((0.5 * scale_x) - wall_thickness, (0.5 * scale_y) - wall_thickness , 0)),
             Vector(((0.5 * scale_x) - wall_thickness, (-0.5 * scale_y) + wall_thickness, 0)),
             Vector(((-0.5 * scale_x) + wall_thickness, (-0.5 * scale_y) + wall_thickness, 0)),
             # 12, 13, 14, 15 - Inside Top Wall
             Vector(((-0.5 * scale_x) + wall_thickness, (0.5 * scale_y) - wall_thickness , 1 * scale_z - wall_thickness)),
             Vector(((0.5 * scale_x) - wall_thickness, (0.5 * scale_y) - wall_thickness , 1 * scale_z - wall_thickness)),
             Vector(((0.5 * scale_x) - wall_thickness, (-0.5 * scale_y) + wall_thickness, 1 * scale_z - wall_thickness)),
             Vector(((-0.5 * scale_x) + wall_thickness, (-0.5 * scale_y) + wall_thickness, 1 * scale_z - wall_thickness)),
            ]

    edges = []
    faces = [
             # Top
             [4, 7, 6, 5],
             # Sides
             [0, 4, 5, 1],
             [3, 7, 4, 0],
             [2, 6, 7, 3],
             [1, 5, 6, 2],
             # Bottom Wall
             [2, 3, 11, 10],
             [0, 8, 11, 3],
             [0, 1, 9, 8],
             [1, 2, 10, 9],
             # Top Wall
             [12, 13, 14, 15],
             # Inside Walls
             [10, 11, 15, 14],
             [9, 10, 14, 13],
             [8, 9, 13, 12],
             [8, 12, 15, 11],
            ]

    # Add studs
    stud_origins = []

    for x in range(0, self.scale[0]):
        for y in range(0, self.scale[1]):
            origin = Vector((
                (h_unit_size / 2 + h_unit_size * float(x)) - float(scale_x) * 0.5,
                (h_unit_size / 2 + h_unit_size * float(y)) - float(scale_y) * 0.5,
                0)
            )
            circle_verts = []

            for i in range(0, stud_segments):
                angle = radians((360 / stud_segments) * i)
                v_bottom = Vector((sin(angle) * stud_radius, cos(angle) * stud_radius, scale_z))
                v_top = v_bottom + Vector((0, 0, 1)) * stud_height
                circle_verts.append(v_bottom - origin)
                circle_verts.append(v_top - origin)
            
            verts.extend(circle_verts)

            print("Length:")
            print(len(verts))
            r_start = len(verts) - stud_segments * 2
            for j in range (r_start, len(verts), 2):
                face = [
                    j,
                    (j - r_start + 1) % 24 + r_start,
                    (j - r_start + 3) % 24 + r_start,
                    (j - r_start + 2) % 24 + r_start
                ]
                print(face)
                faces.append(face)

    mesh = bpy.data.meshes.new(name="New Toy Brick")
    mesh.from_pydata(verts, edges, faces)
    # useful for development when the mesh may be invalid.
    # mesh.validate(verbose=True)
    object_data_add(context, mesh, operator=self)


class OBJECT_OT_add_object(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_object"
    bl_label = "Add Mesh Object"
    bl_options = {'REGISTER', 'UNDO'}

    scale = IntVectorProperty(
            name="scale",
            default=(2.0, 4.0, 1.0),
            soft_min=1,
            # subtype='XYZ',
            description="scaling",
            )

    def execute(self, context):

        add_object(self, context)

        return {'FINISHED'}


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
