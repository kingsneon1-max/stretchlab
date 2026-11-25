# StretchLab - Putaran Bahu v1.0
# Blender Python scene generator.
# This is a PREVISUALIZATION / motion-blockout scene, not a photorealistic final character.
# Run in Blender: Scripting > Open > this file > Run Script.
# Then press Render > Render Animation. Set output path below before rendering.

import bpy
import math
from mathutils import Vector

# -----------------------------
# CONFIGURATION
# -----------------------------
FPS = 60
DURATION_SECONDS = 8
FRAME_END = FPS * DURATION_SECONDS
OUTPUT_PATH = "//StretchLab_Putaran_Bahu_v1.mp4"
RENDER_RESOLUTION = (1920, 1080)
PREVIEW_SAMPLES = 32
FINAL_SAMPLES = 96

# -----------------------------
# CLEAN SCENE
# -----------------------------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.materials, bpy.data.cameras, bpy.data.lights, bpy.data.curves, bpy.data.meshes):
    pass

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = PREVIEW_SAMPLES
scene.render.resolution_x, scene.render.resolution_y = RENDER_RESOLUTION
scene.render.resolution_percentage = 100
scene.render.fps = FPS
scene.frame_start = 1
scene.frame_end = FRAME_END
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'HIGH'
scene.render.filepath = OUTPUT_PATH
scene.world.color = (0.025, 0.035, 0.055)

# Color management
scene.view_settings.view_transform = 'AgX'

# -----------------------------
# MATERIALS
# -----------------------------
def make_mat(name, color, metallic=0.0, roughness=0.45, emission=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*color, 1)
        bsdf.inputs["Emission Strength"].default_value = emission
    return mat

skin = make_mat("Skin - neutral warm", (0.48, 0.29, 0.20), roughness=0.52)
shirt = make_mat("Training shirt - graphite", (0.045, 0.065, 0.09), roughness=0.72)
shorts = make_mat("Training shorts", (0.025, 0.035, 0.05), roughness=0.8)
muscle = make_mat("Target muscle - deltoid highlight", (0.95, 0.12, 0.075), roughness=0.38, emission=0.12)
floor_mat = make_mat("Studio floor", (0.025, 0.04, 0.065), roughness=0.85)
cyan = make_mat("Motion guide cyan", (0.02, 0.48, 0.95), metallic=0.15, emission=1.5)

# -----------------------------
# GEOMETRY HELPERS
# -----------------------------
def uv_sphere(name, loc, scale, mat, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=20, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.shade_smooth()
    obj.data.materials.append(mat)
    if parent:
        obj.parent = parent
        obj.matrix_parent_inverse = parent.matrix_world.inverted()
    return obj

def cylinder_between(name, a, b, radius, mat, vertices=32, parent=None):
    a, b = Vector(a), Vector(b)
    direction = b - a
    mid = (a + b) / 2
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=direction.length, location=mid)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = direction.to_track_quat('Z', 'Y')
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new("Soft anatomical edges", 'BEVEL')
    bevel.width = radius * 0.25
    bevel.segments = 3
    obj.modifiers.new("Weighted normals", 'WEIGHTED_NORMAL')
    if parent:
        obj.parent = parent
        obj.matrix_parent_inverse = parent.matrix_world.inverted()
    return obj

# -----------------------------
# PROCEDURAL HUMAN BLOCKOUT
# -----------------------------
# Coordinate convention: front faces camera at -Y; vertical is Z.
# A replaceable rigged human asset is required for final photorealism.
root = bpy.data.objects.new("HUMAN_ROOT_REPLACE_WITH_RIGGED_CHARACTER", None)
bpy.context.collection.objects.link(root)

# Torso and pelvis
uv_sphere("Torso_blockout", (0, 0, 1.48), (0.39, 0.22, 0.62), shirt, root)
uv_sphere("Pelvis_blockout", (0, 0, 0.92), (0.34, 0.21, 0.25), shorts, root)
uv_sphere("Neck", (0, 0, 2.12), (0.105, 0.105, 0.18), skin, root)
uv_sphere("Head", (0, 0, 2.42), (0.19, 0.18, 0.25), skin, root)

# Legs
for side, x in (("L", -0.17), ("R", 0.17)):
    cylinder_between(f"Thigh_{side}", (x, 0, 0.85), (x, 0, 0.34), 0.105, shorts, parent=root)
    cylinder_between(f"Shin_{side}", (x, 0, 0.34), (x, -0.015, -0.12), 0.075, skin, parent=root)
    uv_sphere(f"Foot_{side}", (x, -0.09, -0.16), (0.09, 0.18, 0.055), shorts, root)

# Shoulder pivot empties and arms; these are animation controls for the blockout.
controls = {}
for side, sign in (("L", -1), ("R", 1)):
    pivot = bpy.data.objects.new(f"Shoulder_CTRL_{side}", None)
    bpy.context.collection.objects.link(pivot)
    pivot.location = (sign * 0.36, 0, 1.92)
    pivot.parent = root
    controls[side] = pivot

    # upper arm and forearm are parented to pivot; geometry is a visual proxy
    upper = cylinder_between(f"UpperArm_{side}", (sign*0.05, 0, -0.02), (sign*0.16, 0, -0.48), 0.085, skin, parent=pivot)
    elbow = uv_sphere(f"Elbow_{side}", (sign*0.16, 0, -0.48), (0.085, 0.085, 0.085), skin, pivot)
    fore = cylinder_between(f"Forearm_{side}", (sign*0.16, 0, -0.48), (sign*0.19, -0.015, -0.91), 0.065, skin, parent=pivot)
    hand = uv_sphere(f"Hand_{side}", (sign*0.19, -0.02, -0.98), (0.075, 0.055, 0.12), skin, pivot)

    # Deltoid highlight cap: a visible target overlay, not a detailed muscle mesh.
    cap = uv_sphere(f"DELTOID_TARGET_OVERLAY_{side}", (sign*0.0, 0, -0.035), (0.135, 0.13, 0.15), muscle, pivot)

# -----------------------------
# SHOULDER ROLL ANIMATION
# -----------------------------
# Cycle: neutral -> shrug -> slight backward roll -> controlled lowering -> neutral.
# The proxy arms follow shoulder pivots; final rig should use scapula/clavicle/upper-arm bones.
keyframes = [
    (1,   (0.0, 0.0, 0.0)),
    (30,  (-0.10, 0.0, 0.0)),
    (60,  (-0.16, 0.0, 0.0)),
    (90,  (-0.13, 0.12, 0.0)),
    (120, (-0.06, 0.22, 0.0)),
    (150, (0.0, 0.12, 0.0)),
    (180, (0.0, 0.0, 0.0)),
    (210, (-0.10, 0.0, 0.0)),
    (240, (-0.16, 0.0, 0.0)),
    (270, (-0.13, 0.12, 0.0)),
    (300, (-0.06, 0.22, 0.0)),
    (330, (0.0, 0.12, 0.0)),
    (360, (0.0, 0.0, 0.0)),
    (FRAME_END, (0.0, 0.0, 0.0)),
]
for side, pivot in controls.items():
    for frame, (xrot, yrot, zrot) in keyframes:
        # Mirror rotation direction slightly for left/right shoulders.
        pivot.rotation_euler = (xrot, yrot * (1 if side == "R" else -1), zrot)
        pivot.keyframe_insert(data_path="rotation_euler", frame=frame)
    if pivot.animation_data and pivot.animation_data.action:
        for fc in pivot.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'BEZIER'
                kp.handle_left_type = 'AUTO_CLAMPED'
                kp.handle_right_type = 'AUTO_CLAMPED'

# -----------------------------
# FLOOR / STUDIO
# -----------------------------
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.23))
floor = bpy.context.object
floor.name = "Studio_Floor"
floor.data.materials.append(floor_mat)

# Lighting
def area_light(name, loc, power, size, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    light = bpy.context.object
    light.name = name
    light.data.energy = power
    light.data.shape = 'DISK'
    light.data.size = size
    light.rotation_euler = (Vector(target) - light.location).to_track_quat('-Z', 'Y').to_euler()
    return light

area_light("Key_softbox", (3, -4, 5), 850, 4.0, (0, 0, 1.3))
area_light("Fill_softbox", (-3, -2, 3), 500, 3.0, (0, 0, 1.4))
area_light("Rim_light", (0, 2, 4), 1000, 2.5, (0, 0, 1.5))

# -----------------------------
# CAMERAS: front, 45-degree, side
# -----------------------------
def add_camera(name, loc, target, lens=55):
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.object
    cam.name = name
    cam.data.lens = lens
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    return cam

cam_front = add_camera("CAM_FRONT", (0, -6.8, 1.55), (0, 0, 1.25), 52)
cam_45 = add_camera("CAM_45_DEG", (4.8, -5.8, 1.65), (0, 0, 1.25), 52)
cam_side = add_camera("CAM_SIDE", (6.8, 0, 1.55), (0, 0, 1.25), 52)

# Multi-angle edit using camera markers. Markers are placed at clear movement phases.
scene.camera = cam_front
for frame, cam, label in [
    (1, cam_front, "Front - neutral and full cycle"),
    (121, cam_45, "45 degree - posterior shoulder path"),
    (241, cam_side, "Side - posture and range"),
]:
    marker = scene.timeline_markers.new(label, frame=frame)
    marker.camera = cam

# Camera cuts are marker-based; in Blender render animation, camera marker switching
# can be enabled in Timeline > Markers > Bind Camera to Markers.
# For a single continuous front-view master, leave CAM_FRONT active.

# -----------------------------
# ANATOMY LABEL (simple 3D text)
# -----------------------------
def add_text(body, loc, size, mat):
    curve = bpy.data.curves.new("Text_" + body, type='FONT')
    curve.body = body
    curve.size = size
    obj = bpy.data.objects.new("Label_" + body, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    obj.data.materials.append(mat)
    return obj

# Text is placed off to the side for a clean teaching layout.
add_text("SHOULDER ROTATION", (-1.45, -0.05, 2.75), 0.16, cyan)
add_text("TARGET: DELTOID", (-1.45, -0.05, 2.53), 0.10, muscle)

# -----------------------------
# RENDER / OUTPUT
# -----------------------------
scene.frame_set(1)
scene.render.image_settings.color_mode = 'RGB'
scene.render.ffmpeg.audio_codec = 'NONE'
scene.cycles.samples = FINAL_SAMPLES

# Save a .blend alongside the MP4 output.
blend_path = bpy.path.abspath("//StretchLab_Putaran_Bahu_v1.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)

print("StretchLab shoulder-roll blockout created.")
print("Saved Blender project:", blend_path)
print("Render output:", bpy.path.abspath(OUTPUT_PATH))
print("IMPORTANT: Replace the procedural blockout with a properly licensed rigged human model")
print("and anatomically correct shoulder/scapula rig before treating this as final exercise guidance.")
