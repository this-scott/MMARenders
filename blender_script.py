import bpy
import numpy as np
import json

armature = bpy.data.objects["SMPLX-mesh"]
pose_data = {}

for bone in armature.pose.bones:
    pose_data[bone.name] = list(bone.rotation_quaternion)

with open("/home/scott/Documents/Workspaces/2025/BoxingRenders/rk.json", "w") as f:
    json.dump(pose_data, f)