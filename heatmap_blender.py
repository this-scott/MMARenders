import bpy
import sys

"""Getting arguments(different bpy because script call)"""
argv = sys.argv
try: 
    index = argv.index("--")
    argv = argv[index + 1:]
except ValueError:
    print("NO CUSTOM ARGS, I AM DUCK PROGRAMMING. THIS WILL CRASH")
    sys.exit(1)

#args should be arrays of four floats, should support sync arms and legs vs regular arms and legs according to # of inputs
print("Argv: ", argv)

"""Process arguments as arrays"""
args = []
currarr = []
for i, arg in enumerate(argv):
    currarr.append(float(arg))
    if (i+1)%3==0:
        currarr.append(1.0)
        args.append(currarr)
        currarr = []

print("Args: ", args)
"""Naming some defaults"""
blend_name = "ReadyPos2.blend"
obj = bpy.data.objects['SMPLX-mesh-male']
vg_names = ['left_elbow', 'right_elbow', 'left_ankle', 'right_ankle']

#if you're wondering why I'm using """ instead of comments,
#it's because they show up in a really pretty font with the panda syntax theme
for i, vg_name in enumerate(vg_names):
    """Creating the material"""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.material_slot_add()

    mat = bpy.data.materials.new(name="Material"+str(i))
    #going to make 4 materials anyway, who cares it's only 4
    if len(args)==3:
        mat.diffuse_color = args[i+1%2]
    else:
        mat.diffuse_color = args[i]

    obj.material_slots[-1].material = mat

    """Getting the vertex group"""
    mat_index = len(obj.material_slots) - 1

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    obj.vertex_groups.active = obj.vertex_groups[vg_name]

    bpy.ops.object.vertex_group_select()

    """Assign material"""
    obj.active_material_index = mat_index
    bpy.ops.object.material_slot_assign()

"""Saving as a png"""
bpy.ops.object.mode_set(mode='OBJECT')
scene = bpy.context.scene
scene.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)
scene.render.filepath = "pictures/temp.png"
scene.render.resolution_x = 600
scene.render.resolution_y = 600
bpy.ops.render.render(write_still=True)

"""Saving scene edits"""
#bpy.ops.wm.save_as_mainfile(filepath=blend_name)
