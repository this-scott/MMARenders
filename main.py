import json
import torch
import smplx
import pyrender
import trimesh
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import sys

# Quaternion to axis-angle conversion function
def quaternion_to_axis_angle(quaternion):
    """
    BLENDER POSING TO SMLPX POSING
    """
    #normalize
    quat = quaternion / torch.norm(quaternion)
    
    #split
    w, x, y, z = quat[0], quat[1], quat[2], quat[3]
    
    #angle
    angle = 2 * torch.acos(torch.clamp(w, -1.0, 1.0))
    
    #axis
    norm = torch.sqrt(1 - w * w)
    
    # Handle the case where the quaternion is close to identity
    if norm < 1e-8:
        return torch.zeros(3, dtype=torch.float32)
    
    #normalized axis
    axis = torch.tensor([x, y, z]) / norm
    
    # Multiply axis by angle to get axis-angle representation
    return axis * angle

def createModelNPose(path,bcf):
    with open(path, "r") as f:
        pose_data = json.load(f)


    model_path = "models"
    model = smplx.create(model_path, model_type="smplx", gender="male", use_pca=False)

    # Create tensors for different pose components
    global_orient = torch.zeros(1, 3)  #root orientation
    body_pose = torch.zeros(1, 21 * 3)  # Body pose
    left_hand_pose = torch.zeros(1, 15 * 3)  # Left hand 
    right_hand_pose = torch.zeros(1, 15 * 3)  # Right hand 
    jaw_pose = torch.zeros(1, 3)  # Jaw
    leye_pose = torch.zeros(1, 3)  # Left eye
    reye_pose = torch.zeros(1, 3)  # Right eye

    # SMPL-X has a specific order for body joints
    body_joint_mapping = {
        "pelvis": 0,
        "left_hip": 1,
        "right_hip": 2,
        "spine1": 3,
        "left_knee": 4,
        "right_knee": 5,
        "spine2": 6,
        "left_ankle": 7,
        "right_ankle": 8,
        "spine3": 9,
        "left_foot": 10,
        "right_foot": 11,
        "neck": 12,
        "left_collar": 13,
        "right_collar": 14,
        "head": 15,
        "left_shoulder": 16,
        "right_shoulder": 17,
        "left_elbow": 18,
        "right_elbow": 19,
        "left_wrist": 20,
        "right_wrist": 21,
    }

    # Hand joint mappings for left and right hands
    left_hand_mapping = {
        "left_index1": 0,
        "left_index2": 1,
        "left_index3": 2,
        "left_middle1": 3,
        "left_middle2": 4,
        "left_middle3": 5,
        "left_pinky1": 6,
        "left_pinky2": 7,
        "left_pinky3": 8,
        "left_ring1": 9,
        "left_ring2": 10,
        "left_ring3": 11,
        "left_thumb1": 12,
        "left_thumb2": 13,
        "left_thumb3": 14,
    }

    right_hand_mapping = {
        "right_index1": 0,
        "right_index2": 1,
        "right_index3": 2,
        "right_middle1": 3,
        "right_middle2": 4,
        "right_middle3": 5,
        "right_pinky1": 6,
        "right_pinky2": 7,
        "right_pinky3": 8,
        "right_ring1": 9,
        "right_ring2": 10,
        "right_ring3": 11,
        "right_thumb1": 12,
        "right_thumb2": 13,
        "right_thumb3": 14,
    }

    # Process each joint from the pose data
    for joint_name, quat in pose_data.items():
        quat_tensor = torch.tensor(quat, dtype=torch.float32)
        axis_angle = quaternion_to_axis_angle(quat_tensor)
        
        if joint_name == "root":
            global_orient[0, :] = axis_angle
        elif joint_name in body_joint_mapping:
            idx = body_joint_mapping[joint_name] - 1  # -1 to not include root
            if 0 <= idx < 21:  
                body_pose[0, idx * 3:(idx + 1) * 3] = axis_angle
        elif joint_name in left_hand_mapping:
            idx = left_hand_mapping[joint_name]
            left_hand_pose[0, idx * 3:(idx + 1) * 3] = axis_angle
        elif joint_name in right_hand_mapping:
            idx = right_hand_mapping[joint_name]
            right_hand_pose[0, idx * 3:(idx + 1) * 3] = axis_angle
        elif joint_name == "jaw":
            jaw_pose[0, :] = axis_angle
        elif joint_name == "left_eye_smplhf":
            leye_pose[0, :] = axis_angle
        elif joint_name == "right_eye_smplhf":
            reye_pose[0, :] = axis_angle
        else:
            print(f"Warning: Joint '{joint_name}' not found in mappings")

    # Apply pose to the SMPL-X model
    output = model(
        global_orient=global_orient,
        body_pose=body_pose,
        left_hand_pose=left_hand_pose,
        right_hand_pose=right_hand_pose,
        jaw_pose=jaw_pose,
        leye_pose=leye_pose,
        reye_pose=reye_pose
    )

    # Render with pyrender
    mesh = output.vertices.detach().cpu().numpy().squeeze()
    faces = model.faces
    tri_mesh = trimesh.Trimesh(vertices=mesh, faces=faces)
    mat = pyrender.MetallicRoughnessMaterial(baseColorFactor=bcf)
    smpl_mesh = pyrender.Mesh.from_trimesh(tri_mesh, material=mat)

    return smpl_mesh

def main():
    #Colormap
    cmap = cm.gist_rainbow

    #Norm to map 1 though 15 to colors
    norm = plt.Normalize(1, 15)

    scene = pyrender.Scene(bg_color=[0.0, 0.0, 0.0, 0.0])
    scene.add(createModelNPose("poses/rightlowkick.json", cmap(norm(8))))
    scene.add(createModelNPose("poses/clinchook.json", cmap(norm(14))))
    scene.add(createModelNPose("poses/jab.json",cmap(norm(10))))

    #camera and lighting
    camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0)
    camera_pose = np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 2.5],
        [0.0, 0.0, 0.0, 1.0]
    ])
    scene.add(camera, pose=camera_pose)
    light = pyrender.DirectionalLight(color=[1.0, 1.0, 1.0], intensity=2.0)
    scene.add(light, pose=camera_pose)

    #IF THERE IS ANY ARG WE DO A 3D RENDER
    if len(sys.argv) > 1:
       viewer = pyrender.Viewer(scene, use_raymond_lighting=True, render_flags={"blend": True, "cull_faces": False})
    else:
        r = pyrender.OffscreenRenderer(600, 600)

        # These flags might not do anything
        flags = pyrender.RenderFlags.RGBA | pyrender.RenderFlags.SKIP_CULL_FACES
        color, depth = r.render(scene, flags=flags)
        plt.figure(figsize=(10, 8))
        plt.imshow(color)

        #separate axis for the colorbar
        #having react flashbacks
        cax = plt.axes([0.92, 0.2, 0.03, 0.6])
        cb = plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax)
        cb.set_label('Value Scale (1-15)')

        plt.savefig('pictures/viz.png')
        plt.close()

        r.delete()

if __name__ == "__main__":
    main()