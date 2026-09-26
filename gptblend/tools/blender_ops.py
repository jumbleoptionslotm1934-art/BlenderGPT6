import bpy
import bmesh
import math
from mathutils import Vector


ALLOWED_PRIMITIVES = {
    "CUBE": bpy.ops.mesh.primitive_cube_add,
    "UV_SPHERE": bpy.ops.mesh.primitive_uv_sphere_add,
    "CYLINDER": bpy.ops.mesh.primitive_cylinder_add,
    "CONE": bpy.ops.mesh.primitive_cone_add,
    "TORUS": bpy.ops.mesh.primitive_torus_add,
    "PLANE": bpy.ops.mesh.primitive_plane_add,
}


def _result(ok, message, **extra):
    data = {"ok": ok, "message": message}
    data.update(extra)
    return data


def _get_object(name):
    obj = bpy.data.objects.get(name)
    if obj is None:
        return None
    scene = bpy.context.scene
    return obj if obj in scene.objects else None


def _collection_in_scene(collection, scene):
    if collection == scene.collection:
        return True
    stack = list(scene.collection.children)
    visited = set()
    while stack:
        current = stack.pop()
        key = current.as_pointer()
        if key in visited:
            continue
        visited.add(key)
        if current == collection:
            return True
        stack.extend(current.children)
    return False


def _get_collection(name, scene=None):
    collection = bpy.data.collections.get(name)
    if collection is None:
        return None
    if scene is None or _collection_in_scene(collection, scene):
        return collection
    return None


def _set_active_only(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def _ensure_object_mode():
    if bpy.context.mode == "OBJECT":
        return None
    try:
        bpy.ops.object.mode_set(mode="OBJECT")
    except RuntimeError as exc:
        return _result(False, f"This tool requires Blender Object Mode: {exc}")
    return None


def _scene_collection_names(scene):
    names = [scene.collection.name]
    stack = list(scene.collection.children)
    visited = set()
    while stack:
        collection = stack.pop()
        if collection in visited:
            continue
        visited.add(collection)
        names.append(collection.name)
        stack.extend(collection.children)
    return names


def inspect_scene():
    scene = bpy.context.scene
    all_objects = list(scene.objects)
    max_objects = 200
    objects = [{
        "name": o.name,
        "type": o.type,
        "location": [round(v, 4) for v in o.location],
        "rotation_degrees": [round(math.degrees(v), 2) for v in o.rotation_euler],
        "scale": [round(v, 4) for v in o.scale],
        "selected": o.select_get(),
        "hidden": o.hide_get(),
        "hidden_from_render": o.hide_render,
        "parent": o.parent.name if o.parent else None,
        "collections": [c.name for c in o.users_collection],
    } for o in all_objects[:max_objects]]
    return _result(
        True,
        "Scene inspected.",
        scene=scene.name,
        mode=bpy.context.mode,
        active_object=bpy.context.active_object.name if bpy.context.active_object else None,
        camera=scene.camera.name if scene.camera else None,
        collections=_scene_collection_names(scene),
        object_count=len(all_objects),
        objects_returned=len(objects),
        truncated=len(all_objects) > max_objects,
        objects=objects,
    )


def create_object(object_type, name, location, scale):
    error = _ensure_object_mode()
    if error:
        return error
    object_type = object_type.upper()
    if object_type not in ALLOWED_PRIMITIVES:
        return _result(False, f"Unsupported primitive: {object_type}")
    if bpy.data.objects.get(name):
        return _result(False, f"An object named '{name}' already exists.")
    bpy.ops.object.select_all(action="DESELECT")
    ALLOWED_PRIMITIVES[object_type](location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    return _result(True, f"Created {obj.name}.", name=obj.name, type=obj.type)


def transform_object(name, location, rotation_degrees, scale):
    obj = _get_object(name)
    if obj is None:
        return _result(False, f"Object '{name}' was not found.")
    obj.location = location
    obj.rotation_euler = [math.radians(v) for v in rotation_degrees]
    obj.scale = scale
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    return _result(True, f"Transformed {obj.name}.", name=obj.name)


def rename_object(current_name, new_name):
    obj = _get_object(current_name)
    if obj is None:
        return _result(False, f"Object '{current_name}' was not found.")
    if current_name != new_name and bpy.data.objects.get(new_name):
        return _result(False, f"An object named '{new_name}' already exists.")
    old_name = obj.name
    obj.name = new_name
    return _result(True, f"Renamed {old_name} to {obj.name}.", name=obj.name)


def delete_object(name):
    obj = _get_object(name)
    if obj is None:
        return _result(False, f"Object '{name}' was not found.")
    bpy.data.objects.remove(obj, do_unlink=True)
    return _result(True, f"Deleted {name}.")


def duplicate_object(name, new_name, location):
    error = _ensure_object_mode()
    if error:
        return error
    source = _get_object(name)
    if source is None:
        return _result(False, f"Object '{name}' was not found.")
    if bpy.data.objects.get(new_name):
        return _result(False, f"An object named '{new_name}' already exists.")
    duplicate = source.copy()
    if source.data:
        duplicate.data = source.data.copy()
    duplicate.name = new_name
    duplicate.location = location
    target_collection = source.users_collection[0] if source.users_collection else bpy.context.collection
    target_collection.objects.link(duplicate)
    _set_active_only(duplicate)
    return _result(True, f"Duplicated {name} as {duplicate.name}.", name=duplicate.name)


# ---------------------------------------------------------------------------
# Additional capabilities
# ---------------------------------------------------------------------------

def inspect_object(name):
    obj = _get_object(name)
    if obj is None:
        return _result(False, f"Object '{name}' was not found.")

    materials = []
    if hasattr(obj.data, "materials"):
        materials = [m.name if m else None for m in obj.data.materials]

    modifiers = [{
        "name": modifier.name,
        "type": modifier.type,
        "show_viewport": modifier.show_viewport,
        "show_render": modifier.show_render,
    } for modifier in obj.modifiers]

    constraints = [{
        "name": constraint.name,
        "type": constraint.type,
        "target": constraint.target.name if getattr(constraint, "target", None) else None,
    } for constraint in obj.constraints]

    animation = None
    if obj.animation_data and obj.animation_data.action:
        action = obj.animation_data.action
        frames = [
            round(point.co.x, 3)
            for fcurve in action.fcurves
            for point in fcurve.keyframe_points
        ]
        animation = {
            "action": action.name,
            "keyframe_count": len(frames),
            "frame_start": min(frames) if frames else None,
            "frame_end": max(frames) if frames else None,
        }

    camera_settings = None
    if obj.type == "CAMERA":
        camera = obj.data
        camera_settings = {
            "lens": float(camera.lens),
            "dof_enabled": bool(camera.dof.use_dof),
            "dof_focus_object": camera.dof.focus_object.name if camera.dof.focus_object else None,
            "dof_focus_distance": float(camera.dof.focus_distance),
            "dof_fstop": float(camera.dof.aperture_fstop),
        }

    return _result(
        True,
        f"Inspected {obj.name}.",
        object={
            "name": obj.name,
            "type": obj.type,
            "location": [round(v, 4) for v in obj.location],
            "rotation_degrees": [round(math.degrees(v), 2) for v in obj.rotation_euler],
            "scale": [round(v, 4) for v in obj.scale],
            "dimensions": [round(v, 4) for v in obj.dimensions],
            "selected": obj.select_get(),
            "color": [round(v, 4) for v in obj.color],
            "hidden": obj.hide_get(),
            "hidden_from_render": obj.hide_render,
            "parent": obj.parent.name if obj.parent else None,
            "collections": [c.name for c in obj.users_collection],
            "materials": materials,
            "modifiers": modifiers,
            "constraints": constraints,
            "animation": animation,
            "camera_settings": camera_settings,
        },
    )


def select_objects(names, clear_existing):
    error = _ensure_object_mode()
    if error:
        return error
    if clear_existing:
        bpy.ops.object.select_all(action="DESELECT")

    missing = []
    selected = []
    for name in names:
        obj = _get_object(name)
        if obj is None:
            missing.append(name)
            continue
        obj.select_set(True)
        selected.append(obj.name)

    if selected:
        bpy.context.view_layer.objects.active = _get_object(selected[-1])

    if missing:
        return _result(
            False,
            f"Some objects were not found: {', '.join(missing)}.",
            selected=selected,
            missing=missing,
        )

    return _result(True, f"Selected {len(selected)} object(s).", selected=selected)


def set_material(object_name, material_name, base_color, metallic, roughness):
    obj = _get_object(object_name)
    if obj is None:
        return _result(False, f"Object '{object_name}' was not found.")
    if not hasattr(obj.data, "materials"):
        return _result(False, f"Object '{object_name}' does not support materials.")

    color = [min(1.0, max(0.0, float(v))) for v in base_color]
    material = bpy.data.materials.get(material_name)
    if material is None:
        material = bpy.data.materials.new(material_name)

    material.use_nodes = True
    material.diffuse_color = color

    principled = material.node_tree.nodes.get("Principled BSDF")
    if principled:
        base_input = principled.inputs.get("Base Color")
        if base_input:
            base_input.default_value = color
        metallic_input = principled.inputs.get("Metallic")
        if metallic_input:
            metallic_input.default_value = float(metallic)
        roughness_input = principled.inputs.get("Roughness")
        if roughness_input:
            roughness_input.default_value = float(roughness)

    if len(obj.data.materials) == 0:
        obj.data.materials.append(material)
    else:
        obj.data.materials[0] = material
    obj.active_material_index = 0

    # Switch visible 3D Viewports to Material Preview so the new material is immediately visible.
    set_viewport_shading("MATERIAL")

    return _result(
        True,
        f"Assigned material '{material.name}' to {obj.name}.",
        object_name=obj.name,
        material_name=material.name,
    )


def set_object_color(name, color):
    obj = _get_object(name)
    if obj is None:
        return _result(False, f"Object '{name}' was not found.")
    obj.color = [min(1.0, max(0.0, float(v))) for v in color]

    # Object display colors are used by Solid shading, so switch visible
    # 3D Viewports to Solid and set their color source to Object.
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        if not screen:
            continue
        for area in screen.areas:
            if area.type == "VIEW_3D":
                shading = area.spaces.active.shading
                shading.type = "SOLID"
                shading.color_type = "OBJECT"

    return _result(True, f"Set viewport color on {obj.name}.", color=list(obj.color))


def add_bevel_modifier(object_name, modifier_name, width, segments, limit_method):
    obj = _get_object(object_name)
    if obj is None:
        return _result(False, f"Object '{object_name}' was not found.")
    if obj.type != "MESH":
        return _result(False, f"Bevel modifiers are only supported for mesh objects, not {obj.type}.")
    if obj.modifiers.get(modifier_name):
        return _result(False, f"Modifier '{modifier_name}' already exists on {obj.name}.")

    modifier = obj.modifiers.new(modifier_name, "BEVEL")
    modifier.width = float(width)
    modifier.segments = int(segments)
    modifier.limit_method = limit_method
    return _result(True, f"Added Bevel modifier '{modifier.name}' to {obj.name}.")


def add_subdivision_modifier(object_name, modifier_name, levels, render_levels):
    obj = _get_object(object_name)
    if obj is None:
        return _result(False, f"Object '{object_name}' was not found.")
    if obj.type != "MESH":
        return _result(False, f"Subdivision is only supported for mesh objects, not {obj.type}.")
    if obj.modifiers.get(modifier_name):
        return _result(False, f"Modifier '{modifier_name}' already exists on {obj.name}.")

    modifier = obj.modifiers.new(modifier_name, "SUBSURF")
    modifier.subdivision_type = "CATMULL_CLARK"
    modifier.levels = int(levels)
    modifier.render_levels = int(render_levels)
    return _result(True, f"Added Subdivision modifier '{modifier.name}' to {obj.name}.")


def remove_modifier(object_name, modifier_name):
    obj = _get_object(object_name)
    if obj is None:
        return _result(False, f"Object '{object_name}' was not found.")
    modifier = obj.modifiers.get(modifier_name)
    if modifier is None:
        return _result(False, f"Modifier '{modifier_name}' was not found on {obj.name}.")
    obj.modifiers.remove(modifier)
    return _result(True, f"Removed modifier '{modifier_name}' from {obj.name}.")


def apply_modifier(object_name, modifier_name):
    obj = _get_object(object_name)
    if obj is None:
        return _result(False, f"Object '{object_name}' was not found.")
    if bpy.context.mode != "OBJECT":
        return _result(False, "Applying modifiers requires Blender Object Mode.")
    if obj.modifiers.get(modifier_name) is None:
        return _result(False, f"Modifier '{modifier_name}' was not found on {obj.name}.")

    _set_active_only(obj)
    try:
        bpy.ops.object.modifier_apply(modifier=modifier_name)
    except RuntimeError as exc:
        return _result(False, f"Could not apply modifier '{modifier_name}': {exc}")

    return _result(True, f"Applied modifier '{modifier_name}' to {obj.name}.")


def shade_object(object_name, smooth):
    obj = _get_object(object_name)
    if obj is None:
        return _result(False, f"Object '{object_name}' was not found.")
    if obj.type != "MESH":
        return _result(False, f"Shading is only supported for mesh objects, not {obj.type}.")

    for polygon in obj.data.polygons:
        polygon.use_smooth = bool(smooth)

    mode = "smooth" if smooth else "flat"
    return _result(True, f"Set {obj.name} to {mode} shading.")


def join_objects(names, active_name):
    if bpy.context.mode != "OBJECT":
        return _result(False, "Joining objects requires Blender Object Mode.")
    if active_name not in names:
        return _result(False, f"Active object '{active_name}' must be included in names.")

    objects = []
    for name in names:
        obj = _get_object(name)
        if obj is None:
            return _result(False, f"Object '{name}' was not found.")
        objects.append(obj)

    object_type = objects[0].type
    if any(obj.type != object_type for obj in objects):
        return _result(False, "All objects being joined must have the same object type.")
    if object_type not in {"MESH", "CURVE", "SURFACE", "FONT", "META"}:
        return _result(False, f"Object type '{object_type}' cannot be joined by this tool.")

    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    active = _get_object(active_name)
    bpy.context.view_layer.objects.active = active

    try:
        bpy.ops.object.join()
    except RuntimeError as exc:
        return _result(False, f"Join failed: {exc}")

    return _result(True, f"Joined {len(objects)} objects into {active.name}.", name=active.name)


def set_origin(object_name, origin_type):
    obj = _get_object(object_name)
    if obj is None:
        return _result(False, f"Object '{object_name}' was not found.")
    if bpy.context.mode != "OBJECT":
        return _result(False, "Setting an origin requires Blender Object Mode.")

    _set_active_only(obj)
    try:
        bpy.ops.object.origin_set(type=origin_type)
    except RuntimeError as exc:
        return _result(False, f"Could not set origin: {exc}")

    return _result(True, f"Set origin of {obj.name} using {origin_type}.")


def parent_object(child_name, parent_name):
    child = _get_object(child_name)
    parent = _get_object(parent_name)
    if child is None:
        return _result(False, f"Child object '{child_name}' was not found.")
    if parent is None:
        return _result(False, f"Parent object '{parent_name}' was not found.")
    if child == parent:
        return _result(False, "An object cannot parent itself.")
    ancestor = parent
    while ancestor is not None:
        if ancestor == child:
            return _result(False, f"Parenting '{child.name}' to '{parent.name}' would create a cycle.")
        ancestor = ancestor.parent

    child_world = child.matrix_world.copy()
    child.parent = parent
    child.matrix_world = child_world
    return _result(True, f"Parented {child.name} to {parent.name}.")


def hide_object(name, hidden):
    obj = _get_object(name)
    if obj is None:
        return _result(False, f"Object '{name}' was not found.")
    obj.hide_set(bool(hidden))
    return _result(True, f"{'Hidden' if hidden else 'Unhidden'} {obj.name} in the viewport.")


def set_render_visibility(name, hidden_from_render):
    obj = _get_object(name)
    if obj is None:
        return _result(False, f"Object '{name}' was not found.")
    obj.hide_render = bool(hidden_from_render)
    return _result(
        True,
        f"{'Disabled' if hidden_from_render else 'Enabled'} {obj.name} for rendering.",
    )


def create_collection(name, parent_collection_name):
    if bpy.data.collections.get(name):
        return _result(False, f"A collection named '{name}' already exists.")

    scene = bpy.context.scene
    if parent_collection_name == "Scene Collection":
        parent = scene.collection
    else:
        parent = _get_collection(parent_collection_name, scene)

    if parent is None:
        return _result(False, f"Parent collection '{parent_collection_name}' was not found.")

    collection = bpy.data.collections.new(name)
    parent.children.link(collection)
    return _result(True, f"Created collection '{collection.name}'.", name=collection.name)


def move_object_to_collection(object_name, collection_name):
    obj = _get_object(object_name)
    collection = _get_collection(collection_name, bpy.context.scene)
    if obj is None:
        return _result(False, f"Object '{object_name}' was not found.")
    if collection is None:
        return _result(False, f"Collection '{collection_name}' was not found.")

    for current_collection in list(obj.users_collection):
        current_collection.objects.unlink(obj)
    collection.objects.link(obj)
    return _result(True, f"Moved {obj.name} to collection '{collection.name}'.")


def create_light(name, light_type, location, rotation_degrees, energy, color, size):
    error = _ensure_object_mode()
    if error:
        return error
    if bpy.data.objects.get(name):
        return _result(False, f"An object named '{name}' already exists.")

    light_data = bpy.data.lights.new(name=name, type=light_type)
    light_data.energy = float(energy)
    light_data.color = [min(1.0, max(0.0, float(v))) for v in color]

    if light_type == "AREA":
        light_data.shape = "DISK"
        light_data.size = float(size)
    elif light_type in {"POINT", "SPOT"}:
        light_data.shadow_soft_size = float(size)

    light_object = bpy.data.objects.new(name=name, object_data=light_data)
    bpy.context.scene.collection.objects.link(light_object)
    light_object.location = location
    light_object.rotation_euler = [math.radians(v) for v in rotation_degrees]
    _set_active_only(light_object)

    return _result(
        True,
        f"Created {light_type} light '{light_object.name}'.",
        name=light_object.name,
    )


def create_camera(name, location, rotation_degrees, lens, make_active):
    error = _ensure_object_mode()
    if error:
        return error
    if bpy.data.objects.get(name):
        return _result(False, f"An object named '{name}' already exists.")

    camera_data = bpy.data.cameras.new(name=name)
    camera_data.lens = float(lens)
    camera_object = bpy.data.objects.new(name=name, object_data=camera_data)
    bpy.context.scene.collection.objects.link(camera_object)
    camera_object.location = location
    camera_object.rotation_euler = [math.radians(v) for v in rotation_degrees]

    if make_active:
        bpy.context.scene.camera = camera_object

    _set_active_only(camera_object)
    return _result(
        True,
        f"Created camera '{camera_object.name}'." + (" It is now the active scene camera." if make_active else ""),
        name=camera_object.name,
    )


def set_world_background(color, strength):
    scene = bpy.context.scene
    world = scene.world
    if world is None:
        world = bpy.data.worlds.new(f"{scene.name} World")
        scene.world = world

    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    if background is None:
        return _result(False, "The world Background node could not be found.")

    rgb = [min(1.0, max(0.0, float(v))) for v in color]
    background.inputs["Color"].default_value = [rgb[0], rgb[1], rgb[2], 1.0]
    background.inputs["Strength"].default_value = float(strength)

    return _result(True, "Updated the world background.", color=rgb, strength=float(strength))


def create_text(name, body, location, rotation_degrees, size, extrude):
    error = _ensure_object_mode()
    if error:
        return error
    if bpy.data.objects.get(name):
        return _result(False, f"An object named '{name}' already exists.")

    curve = bpy.data.curves.new(name=name, type="FONT")
    curve.body = body
    curve.size = float(size)
    curve.extrude = float(extrude)
    curve.align_x = "CENTER"

    text_object = bpy.data.objects.new(name=name, object_data=curve)
    bpy.context.scene.collection.objects.link(text_object)
    text_object.location = location
    text_object.rotation_euler = [math.radians(v) for v in rotation_degrees]
    _set_active_only(text_object)

    return _result(True, f"Created text object '{text_object.name}'.", name=text_object.name)

def move_object_delta(name, offset):
    obj = _get_object(name)
    if obj is None:
        return _result(False, f"Object '{name}' was not found.")
    obj.location.x += float(offset[0])
    obj.location.y += float(offset[1])
    obj.location.z += float(offset[2])
    return _result(True, f"Moved {obj.name} by {offset}.", location=list(obj.location))


def rotate_object_delta(name, rotation_delta_degrees):
    obj = _get_object(name)
    if obj is None:
        return _result(False, f"Object '{name}' was not found.")
    for index, degrees in enumerate(rotation_delta_degrees):
        obj.rotation_euler[index] += math.radians(float(degrees))
    return _result(True, f"Rotated {obj.name} by {rotation_delta_degrees} degrees.")


def set_object_dimensions(name, dimensions):
    obj = _get_object(name)
    if obj is None:
        return _result(False, f"Object '{name}' was not found.")
    dims = [max(0.0001, float(v)) for v in dimensions]
    try:
        obj.dimensions = dims
    except (TypeError, ValueError) as exc:
        return _result(False, f"Could not set dimensions on {obj.name}: {exc}")
    return _result(True, f"Set dimensions of {obj.name}.", dimensions=list(obj.dimensions))


def apply_object_scale(name):
    obj = _get_object(name)
    if obj is None:
        return _result(False, f"Object '{name}' was not found.")
    if bpy.context.mode != "OBJECT":
        return _result(False, "Applying scale requires Blender Object Mode.")
    _set_active_only(obj)
    try:
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    except RuntimeError as exc:
        return _result(False, f"Could not apply scale: {exc}")
    return _result(True, f"Applied scale on {obj.name}.")


def batch_transform_objects(names, location_offset, rotation_delta_degrees, scale_multiplier):
    missing = []
    changed = []
    offset = [float(v) for v in location_offset]
    rotation = [math.radians(float(v)) for v in rotation_delta_degrees]
    scale = [float(v) for v in scale_multiplier]

    for name in names:
        obj = _get_object(name)
        if obj is None:
            missing.append(name)
            continue
        obj.location = [obj.location[i] + offset[i] for i in range(3)]
        obj.rotation_euler = [obj.rotation_euler[i] + rotation[i] for i in range(3)]
        obj.scale = [obj.scale[i] * scale[i] for i in range(3)]
        changed.append(obj.name)

    if missing:
        return _result(False, f"Some objects were not found: {', '.join(missing)}.", changed=changed, missing=missing)
    return _result(True, f"Batch-transformed {len(changed)} objects.", changed=changed)


def arrange_objects_linear(names, axis, start, spacing, preserve_other_axes):
    objects = []
    missing = []
    for name in names:
        obj = _get_object(name)
        if obj is None:
            missing.append(name)
        else:
            objects.append(obj)

    if missing:
        return _result(False, f"Some objects were not found: {', '.join(missing)}.", missing=missing)

    axis_index = {"X": 0, "Y": 1, "Z": 2}[axis]
    for index, obj in enumerate(objects):
        if preserve_other_axes:
            obj.location[axis_index] = float(start) + index * float(spacing)
        else:
            location = [0.0, 0.0, 0.0]
            location[axis_index] = float(start) + index * float(spacing)
            obj.location = location

    return _result(True, f"Arranged {len(objects)} objects along {axis}.", objects=[o.name for o in objects])


def align_objects(names, axis, mode):
    objects = []
    missing = []
    for name in names:
        obj = _get_object(name)
        if obj is None:
            missing.append(name)
        else:
            objects.append(obj)

    if missing:
        return _result(False, f"Some objects were not found: {', '.join(missing)}.", missing=missing)

    axis_index = {"X": 0, "Y": 1, "Z": 2}[axis]
    values = [obj.location[axis_index] for obj in objects]
    if mode == "MIN":
        target = min(values)
    elif mode == "MAX":
        target = max(values)
    else:
        target = (min(values) + max(values)) / 2.0

    for obj in objects:
        obj.location[axis_index] = target

    return _result(True, f"Aligned {len(objects)} objects on {axis} using {mode}.", value=target)


def distribute_objects(names, axis):
    objects = []
    missing = []
    for name in names:
        obj = _get_object(name)
        if obj is None:
            missing.append(name)
        else:
            objects.append(obj)

    if missing:
        return _result(False, f"Some objects were not found: {', '.join(missing)}.", missing=missing)
    if len(objects) < 3:
        return _result(False, "At least three objects are required to distribute them.")

    axis_index = {"X": 0, "Y": 1, "Z": 2}[axis]
    objects = sorted(objects, key=lambda obj: obj.location[axis_index])
    first = objects[0].location[axis_index]
    last = objects[-1].location[axis_index]
    step = (last - first) / (len(objects) - 1)

    for index, obj in enumerate(objects):
        obj.location[axis_index] = first + step * index

    return _result(True, f"Distributed {len(objects)} objects on {axis}.")


def create_empty(name, empty_type, location, size):
    error = _ensure_object_mode()
    if error:
        return error
    if bpy.data.objects.get(name):
        return _result(False, f"An object named '{name}' already exists.")

    empty = bpy.data.objects.new(name=name, object_data=None)
    bpy.context.scene.collection.objects.link(empty)
    empty.empty_display_type = empty_type
    empty.empty_display_size = float(size)
    empty.location = location
    _set_active_only(empty)
    return _result(True, f"Created Empty '{empty.name}'.", name=empty.name)


def create_bezier_curve(name, location, scale, bevel_depth, bevel_resolution):
    error = _ensure_object_mode()
    if error:
        return error
    if bpy.data.objects.get(name):
        return _result(False, f"An object named '{name}' already exists.")

    bpy.ops.curve.primitive_bezier_curve_add(location=location)
    curve_object = bpy.context.object
    curve_object.name = name
    curve_object.scale = scale
    curve_data = curve_object.data
    curve_data.dimensions = "3D"
    curve_data.bevel_depth = float(bevel_depth)
    curve_data.bevel_resolution = int(bevel_resolution)
    _set_active_only(curve_object)
    return _result(True, f"Created Bezier curve '{curve_object.name}'.", name=curve_object.name)


def _ensure_mesh_modifier_object(object_name, modifier_name, modifier_type):
    obj = _get_object(object_name)
    if obj is None:
        return None, _result(False, f"Object '{object_name}' was not found.")
    if obj.type != "MESH":
        return None, _result(False, f"'{object_name}' must be a mesh object.")
    if obj.modifiers.get(modifier_name):
        return None, _result(False, f"Modifier '{modifier_name}' already exists on {object_name}.")
    return obj, None


def add_array_modifier(object_name, modifier_name, count, relative_offset):
    obj, error = _ensure_mesh_modifier_object(object_name, modifier_name, "ARRAY")
    if error:
        return error
    modifier = obj.modifiers.new(modifier_name, "ARRAY")
    modifier.count = int(count)
    modifier.use_relative_offset = True
    modifier.relative_offset_displace = tuple(float(v) for v in relative_offset)
    return _result(True, f"Added Array modifier '{modifier.name}' to {obj.name}.")


def add_mirror_modifier(object_name, modifier_name, use_x, use_y, use_z, use_clip):
    obj, error = _ensure_mesh_modifier_object(object_name, modifier_name, "MIRROR")
    if error:
        return error
    if not any((use_x, use_y, use_z)):
        return _result(False, "At least one Mirror axis must be enabled.")
    modifier = obj.modifiers.new(modifier_name, "MIRROR")
    modifier.use_axis[0] = bool(use_x)
    modifier.use_axis[1] = bool(use_y)
    modifier.use_axis[2] = bool(use_z)
    modifier.use_clip = bool(use_clip)
    return _result(True, f"Added Mirror modifier '{modifier.name}' to {obj.name}.")


def add_solidify_modifier(object_name, modifier_name, thickness, offset):
    obj, error = _ensure_mesh_modifier_object(object_name, modifier_name, "SOLIDIFY")
    if error:
        return error
    modifier = obj.modifiers.new(modifier_name, "SOLIDIFY")
    modifier.thickness = float(thickness)
    modifier.offset = float(offset)
    return _result(True, f"Added Solidify modifier '{modifier.name}' to {obj.name}.")


def add_boolean_modifier(object_name, modifier_name, operand_name, operation):
    obj, error = _ensure_mesh_modifier_object(object_name, modifier_name, "BOOLEAN")
    if error:
        return error
    operand = _get_object(operand_name)
    if operand is None:
        return _result(False, f"Operand object '{operand_name}' was not found.")
    if operand.type != "MESH":
        return _result(False, f"Operand '{operand_name}' must be a mesh object.")
    if obj == operand:
        return _result(False, "Boolean object and operand must be different objects.")

    modifier = obj.modifiers.new(modifier_name, "BOOLEAN")
    modifier.operation = operation
    modifier.solver = "EXACT"
    modifier.object = operand
    return _result(True, f"Added Boolean {operation} modifier '{modifier.name}' to {obj.name} using {operand.name}.")


def add_shrinkwrap_modifier(object_name, modifier_name, target_name, offset):
    obj, error = _ensure_mesh_modifier_object(object_name, modifier_name, "SHRINKWRAP")
    if error:
        return error
    target = _get_object(target_name)
    if target is None:
        return _result(False, f"Target object '{target_name}' was not found.")
    modifier = obj.modifiers.new(modifier_name, "SHRINKWRAP")
    modifier.target = target
    modifier.offset = float(offset)
    return _result(True, f"Added Shrinkwrap modifier '{modifier.name}' to {obj.name} targeting {target.name}.")


def add_simple_deform_modifier(object_name, modifier_name, deform_method, deform_axis, angle_degrees):
    obj, error = _ensure_mesh_modifier_object(object_name, modifier_name, "SIMPLE_DEFORM")
    if error:
        return error
    modifier = obj.modifiers.new(modifier_name, "SIMPLE_DEFORM")
    modifier.deform_method = deform_method
    modifier.deform_axis = deform_axis
    modifier.angle = math.radians(float(angle_degrees))
    return _result(True, f"Added {deform_method} Simple Deform modifier '{modifier.name}' to {obj.name}.")


def add_decimate_modifier(object_name, modifier_name, ratio):
    obj, error = _ensure_mesh_modifier_object(object_name, modifier_name, "DECIMATE")
    if error:
        return error
    modifier = obj.modifiers.new(modifier_name, "DECIMATE")
    modifier.ratio = float(ratio)
    return _result(True, f"Added Decimate modifier '{modifier.name}' to {obj.name}.", ratio=float(ratio))


def add_weighted_normal_modifier(object_name, modifier_name, keep_sharp):
    obj, error = _ensure_mesh_modifier_object(object_name, modifier_name, "WEIGHTED_NORMAL")
    if error:
        return error
    modifier = obj.modifiers.new(modifier_name, "WEIGHTED_NORMAL")
    modifier.keep_sharp = bool(keep_sharp)
    return _result(True, f"Added Weighted Normal modifier '{modifier.name}' to {obj.name}.")


def aim_object_at(object_name, target_name):
    obj = _get_object(object_name)
    target = _get_object(target_name)
    if obj is None:
        return _result(False, f"Object '{object_name}' was not found.")
    if target is None:
        return _result(False, f"Target object '{target_name}' was not found.")

    direction = target.matrix_world.translation - obj.matrix_world.translation
    if direction.length < 0.000001:
        return _result(False, "Object and target are at the same location.")

    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    return _result(True, f"Aimed {obj.name} at {target.name}.")


def set_render_settings(engine, resolution_x, resolution_y, resolution_percentage, fps):
    scene = bpy.context.scene
    try:
        scene.render.engine = engine
    except (TypeError, ValueError) as exc:
        return _result(False, f"Unsupported render engine '{engine}': {exc}")

    scene.render.resolution_x = int(resolution_x)
    scene.render.resolution_y = int(resolution_y)
    scene.render.resolution_percentage = int(resolution_percentage)
    scene.render.fps = float(fps)
    return _result(
        True,
        "Updated render settings.",
        engine=scene.render.engine,
        resolution=[scene.render.resolution_x, scene.render.resolution_y],
        resolution_percentage=scene.render.resolution_percentage,
        fps=scene.render.fps,
    )






def set_procedural_texture(
    object_name,
    material_name,
    texture_type,
    color_a,
    color_b,
    scale,
    detail,
    roughness,
    bump_strength,
):
    obj = _get_object(object_name)
    if obj is None:
        return _result(False, f"Object '{object_name}' was not found.")
    if not hasattr(obj.data, "materials"):
        return _result(False, f"Object '{object_name}' does not support materials.")

    texture_type = texture_type.upper()
    texture_nodes = {
        "NOISE": "ShaderNodeTexNoise",
        "VORONOI": "ShaderNodeTexVoronoi",
        "WAVE": "ShaderNodeTexWave",
        "BRICK": "ShaderNodeTexBrick",
    }
    node_type = texture_nodes.get(texture_type)
    if not node_type:
        return _result(False, f"Unsupported procedural texture type: {texture_type}")

    material = bpy.data.materials.get(material_name) or bpy.data.materials.new(material_name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    principled = nodes.new("ShaderNodeBsdfPrincipled")
    texcoord = nodes.new("ShaderNodeTexCoord")
    ramp = nodes.new("ShaderNodeValToRGB")
    bump = nodes.new("ShaderNodeBump")

    output.location = (600, 0)
    principled.location = (360, 0)
    bump.location = (120, -180)
    ramp.location = (-120, 120)
    texcoord.location = (-620, 0)

    texture = nodes.new(node_type)
    texture.location = (-360, 100)
    texture.label = f"GPT Blend {texture_type} Texture"

    texture_inputs = texture.inputs
    if texture_inputs.get("Scale"):
        texture_inputs["Scale"].default_value = float(scale)
    if texture_inputs.get("Detail"):
        texture_inputs["Detail"].default_value = float(detail)
    if texture_inputs.get("Roughness"):
        texture_inputs["Roughness"].default_value = float(roughness)

    if texture_type == "BRICK":
        if texture_inputs.get("Color1"):
            texture_inputs["Color1"].default_value = [min(1, max(0, float(v))) for v in color_a]
        if texture_inputs.get("Color2"):
            texture_inputs["Color2"].default_value = [min(1, max(0, float(v))) for v in color_b]
    else:
        ramp.color_ramp.elements[0].position = 0.25
        ramp.color_ramp.elements[0].color = [min(1, max(0, float(v))) for v in color_a]
        ramp.color_ramp.elements[1].position = 0.75
        ramp.color_ramp.elements[1].color = [min(1, max(0, float(v))) for v in color_b]

    links.new(texcoord.outputs["Generated"], texture.inputs["Vector"])

    texture_color = texture.outputs.get("Color")
    texture_factor = texture.outputs.get("Fac")
    if texture_type == "BRICK" and texture_color:
        links.new(texture_color, principled.inputs["Base Color"])
    elif texture_color:
        links.new(texture_color, ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], principled.inputs["Base Color"])
    elif texture_factor:
        links.new(texture_factor, ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], principled.inputs["Base Color"])

    if texture_factor and bump_strength > 0:
        links.new(texture_factor, bump.inputs["Height"])
        bump.inputs["Strength"].default_value = float(bump_strength)
        bump.inputs["Distance"].default_value = 0.15
        links.new(bump.outputs["Normal"], principled.inputs["Normal"])

    if principled.inputs.get("Roughness"):
        principled.inputs["Roughness"].default_value = float(roughness)

    links.new(principled.outputs["BSDF"], output.inputs["Surface"])

    if len(obj.data.materials) == 0:
        obj.data.materials.append(material)
    else:
        obj.data.materials[0] = material
    obj.active_material_index = 0

    # Switch visible 3D Viewports to Material Preview so procedural textures are visible immediately.
    set_viewport_shading("MATERIAL")

    return _result(
        True,
        f"Applied a visible {texture_type.lower()} procedural texture to {obj.name}.",
        object_name=obj.name,
        material_name=material.name,
        texture_type=texture_type,
    )


def set_viewport_shading(shading_type):
    shading_type = shading_type.upper()
    if shading_type not in {"SOLID", "MATERIAL", "RENDERED"}:
        return _result(False, f"Unsupported viewport shading type: {shading_type}")

    changed = 0
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        if not screen:
            continue
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.spaces.active.shading.type = shading_type
                changed += 1

    if changed == 0:
        return _result(False, "No visible 3D Viewport areas were found.")
    return _result(True, f"Set {changed} 3D Viewport(s) to {shading_type.lower()} shading.")

# ---------------------------------------------------------------------------
# Edit Mode / UV workflow tools
# ---------------------------------------------------------------------------

def _prepare_edit_mesh(object_name):
    obj = _get_object(object_name)
    if obj is None:
        return None, None, _result(False, f"Object '{object_name}' was not found.")
    if obj.type != "MESH":
        return None, None, _result(False, f"Object '{object_name}' must be a mesh.")
    try:
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        _set_active_only(obj)
        bpy.ops.object.mode_set(mode="EDIT")
        return obj, bmesh.from_edit_mesh(obj.data), None
    except Exception as exc:
        return None, None, _result(False, f"Could not enter Edit Mode for '{object_name}': {exc}")


def select_mesh_elements(object_name, domain, indices, extend):
    obj, bm, error = _prepare_edit_mesh(object_name)
    if error:
        return error

    try:
        domain = domain.upper()
        if not extend:
            for collection in (bm.verts, bm.edges, bm.faces):
                for element in collection:
                    element.select = False

        collection = {
            "VERT": bm.verts,
            "EDGE": bm.edges,
            "FACE": bm.faces,
        }.get(domain)
        if collection is None:
            return _result(False, "Domain must be VERT, EDGE, or FACE.")

        collection.ensure_lookup_table()
        selected = 0
        missing = []
        for index in indices:
            index = int(index)
            if 0 <= index < len(collection):
                collection[index].select = True
                selected += 1
            else:
                missing.append(index)

        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)
        return _result(
            True,
            f"Selected {selected} {domain.lower()} element(s) on {obj.name}.",
            selected=selected,
            missing_indices=missing,
        )
    finally:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass


def set_mesh_selection_mode(mode):
    mode = mode.upper()
    modes = {
        "VERT": (True, False, False),
        "EDGE": (False, True, False),
        "FACE": (False, False, True),
    }
    selection_mode = modes.get(mode)
    if selection_mode is None:
        return _result(False, "Mesh selection mode must be VERT, EDGE, or FACE.")

    bpy.context.tool_settings.mesh_select_mode = selection_mode
    return _result(True, f"Mesh selection mode set to {mode.lower()}.")


def merge_selected_vertices(object_name, distance):
    obj, bm, error = _prepare_edit_mesh(object_name)
    if error:
        return error

    try:
        verts = [vert for vert in bm.verts if vert.select]
        if not verts:
            return _result(False, f"No selected vertices on {obj.name}.")
        bmesh.ops.remove_doubles(bm, verts=verts, dist=float(distance))
        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=True)
        return _result(True, f"Merged selected vertices on {obj.name}.", vertex_count=len(verts))
    finally:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass


def dissolve_selected(object_name):
    obj, bm, error = _prepare_edit_mesh(object_name)
    if error:
        return error

    try:
        faces = [face for face in bm.faces if face.select]
        edges = [edge for edge in bm.edges if edge.select]
        verts = [vert for vert in bm.verts if vert.select]
        if faces:
            bmesh.ops.dissolve_faces(bm, faces=faces, use_verts=False)
            action = f"Dissolved {len(faces)} face(s)"
        elif edges:
            bmesh.ops.dissolve_edges(bm, edges=edges, use_verts=False, use_face_split=False)
            action = f"Dissolved {len(edges)} edge(s)"
        elif verts:
            bmesh.ops.dissolve_verts(bm, verts=verts, use_face_split=False)
            action = f"Dissolved {len(verts)} vertex/vertices"
        else:
            return _result(False, f"No selected mesh elements on {obj.name}.")

        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=True)
        return _result(True, f"{action} on {obj.name}.")
    finally:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass


def extrude_selected_faces(object_name, offset):
    obj, bm, error = _prepare_edit_mesh(object_name)
    if error:
        return error

    try:
        faces = [face for face in bm.faces if face.select]
        if not faces:
            return _result(False, f"No selected faces on {obj.name}.")
        result = bmesh.ops.extrude_face_region(bm, geom=faces)
        new_verts = [element for element in result.get("geom", []) if isinstance(element, bmesh.types.BMVert)]
        delta = Vector(tuple(float(v) for v in offset))
        bmesh.ops.translate(bm, vec=delta, verts=new_verts)
        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=True)
        return _result(
            True,
            f"Extruded {len(faces)} selected face(s) on {obj.name}.",
            offset=list(delta),
        )
    finally:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass


def unwrap_uv(object_name, method):
    obj, bm, error = _prepare_edit_mesh(object_name)
    if error:
        return error

    try:
        for face in bm.faces:
            face.select = True
        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)

        method = method.upper()
        if method == "SMART_PROJECT":
            result = bpy.ops.uv.smart_project()
        elif method == "ANGLE_BASED":
            result = bpy.ops.uv.unwrap(method="ANGLE_BASED")
        else:
            return _result(False, "UV unwrap method must be SMART_PROJECT or ANGLE_BASED.")

        if "FINISHED" not in result:
            return _result(False, f"UV unwrap did not finish for {obj.name}.")
        return _result(True, f"UV unwrapped {obj.name} using {method.lower()}.")
    except Exception as exc:
        return _result(False, f"UV unwrap failed for {obj.name}: {exc}")
    finally:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass



# ---------------------------------------------------------------------------
# Animation workflow tools
# ---------------------------------------------------------------------------

def set_animation_timing(fps, start_frame, end_frame, current_frame):
    scene = bpy.context.scene
    start_frame = int(start_frame)
    end_frame = int(end_frame)
    current_frame = int(current_frame)

    if start_frame < 1:
        return _result(False, "Start frame must be at least 1.")
    if end_frame < start_frame:
        return _result(False, "End frame must be greater than or equal to start frame.")
    if current_frame < start_frame or current_frame > end_frame:
        return _result(False, "Current frame must be inside the animation range.")
    if float(fps) <= 0:
        return _result(False, "FPS must be greater than 0.")

    scene.render.fps = float(fps)
    scene.frame_start = start_frame
    scene.frame_end = end_frame
    scene.frame_set(current_frame)

    return _result(
        True,
        "Updated animation timing.",
        fps=float(scene.render.fps),
        start_frame=scene.frame_start,
        end_frame=scene.frame_end,
        current_frame=scene.frame_current,
    )


def animate_object_transform(object_name, keyframes, clear_existing):
    obj = _get_object(object_name)
    if obj is None:
        return _result(False, f"Object '{object_name}' was not found.")
    if not keyframes:
        return _result(False, "At least one keyframe is required.")

    error = _ensure_object_mode()
    if error:
        return error

    scene = bpy.context.scene
    original_frame = scene.frame_current
    interpolation_allowed = {
        "BEZIER", "LINEAR", "CONSTANT", "SINE", "QUAD", "CUBIC",
        "QUART", "QUINT", "EXPO", "CIRC", "BACK", "BOUNCE", "ELASTIC",
    }

    try:
        if clear_existing:
            obj.animation_data_clear()

        normalized = []
        for keyframe in keyframes:
            frame = int(keyframe["frame"])
            if frame < 1:
                return _result(False, f"Invalid keyframe frame {frame}. Frames must be at least 1.")

            interpolation = str(keyframe.get("interpolation", "BEZIER")).upper()
            if interpolation not in interpolation_allowed:
                return _result(False, f"Unsupported interpolation '{interpolation}'.")

            location = [float(v) for v in keyframe["location"]]
            rotation = [math.radians(float(v)) for v in keyframe["rotation_degrees"]]
            scale = [float(v) for v in keyframe["scale"]]
            normalized.append((frame, location, rotation, scale, interpolation))

        normalized.sort(key=lambda item: item[0])

        if len(normalized) > 1 and len({item[0] for item in normalized}) != len(normalized):
            return _result(False, "Keyframes must use distinct frame numbers.")

        for frame, location, rotation, scale, interpolation in normalized:
            scene.frame_set(frame)
            obj.location = location
            obj.rotation_euler = rotation
            obj.scale = scale

            obj.keyframe_insert(data_path="location", frame=frame, group="GPT Blend Transform")
            obj.keyframe_insert(data_path="rotation_euler", frame=frame, group="GPT Blend Transform")
            obj.keyframe_insert(data_path="scale", frame=frame, group="GPT Blend Transform")

        action = obj.animation_data.action if obj.animation_data else None
        if action:
            for fcurve in action.fcurves:
                for key in fcurve.keyframe_points:
                    key_frame = int(round(key.co.x))
                    for authored_frame, _, _, _, interpolation in normalized:
                        if key_frame == authored_frame:
                            key.interpolation = interpolation
                            break

        scene.frame_set(max(scene.frame_start, min(original_frame, scene.frame_end)))

        return _result(
            True,
            f"Animated {obj.name} with {len(normalized)} transform keyframe(s).",
            object_name=obj.name,
            keyframes=[frame for frame, _, _, _, _ in normalized],
            start_frame=normalized[0][0],
            end_frame=normalized[-1][0],
            interpolation_summary=sorted({item[4] for item in normalized}),
        )
    except Exception as exc:
        try:
            scene.frame_set(max(scene.frame_start, min(original_frame, scene.frame_end)))
        except Exception:
            pass
        return _result(False, f"Could not animate '{obj.name}': {exc}")


def clear_object_animation(object_name):
    obj = _get_object(object_name)
    if obj is None:
        return _result(False, f"Object '{object_name}' was not found.")

    had_animation = bool(obj.animation_data)
    obj.animation_data_clear()
    return _result(
        True,
        f"Cleared animation from {obj.name}." if had_animation else f"{obj.name} had no animation to clear.",
        had_animation=had_animation,
    )


def set_animation_interpolation(object_name, interpolation):
    obj = _get_object(object_name)
    if obj is None:
        return _result(False, f"Object '{object_name}' was not found.")
    if not obj.animation_data or not obj.animation_data.action:
        return _result(False, f"Object '{obj.name}' has no action to edit.")

    interpolation = str(interpolation).upper()
    allowed = {
        "BEZIER", "LINEAR", "CONSTANT", "SINE", "QUAD", "CUBIC",
        "QUART", "QUINT", "EXPO", "CIRC", "BACK", "BOUNCE", "ELASTIC",
    }
    if interpolation not in allowed:
        return _result(False, f"Unsupported interpolation '{interpolation}'.")

    changed = 0
    for fcurve in obj.animation_data.action.fcurves:
        for key in fcurve.keyframe_points:
            key.interpolation = interpolation
            changed += 1

    return _result(
        True,
        f"Set {changed} animation keyframe point(s) on {obj.name} to {interpolation.lower()} interpolation.",
        keyframes_changed=changed,
    )

def inspect_animation(object_name):
    obj = _get_object(object_name)
    if obj is None:
        return _result(False, f"Object '{object_name}' was not found.")
    action = obj.animation_data.action if obj.animation_data else None
    if action is None:
        return _result(True, f"Object '{obj.name}' has no animation action.", animated=False, object_name=obj.name)

    frames = set()
    fcurves = []
    for fcurve in action.fcurves:
        key_frames = [round(point.co.x, 3) for point in fcurve.keyframe_points]
        frames.update(int(round(frame)) for frame in key_frames)
        fcurves.append({
            "data_path": fcurve.data_path,
            "array_index": fcurve.array_index,
            "keyframe_count": len(key_frames),
            "frames": key_frames,
        })

    return _result(
        True,
        f"Inspected animation on {obj.name}.",
        animated=True,
        object_name=obj.name,
        action=action.name,
        frame_start=min(frames) if frames else None,
        frame_end=max(frames) if frames else None,
        keyframe_count=sum(len(curve["frames"]) for curve in fcurves),
        fcurves=fcurves,
    )


# ---------------------------------------------------------------------------
# Camera, constraints, animation-loop, and timeline tools
# ---------------------------------------------------------------------------

def set_camera_depth_of_field(camera_name, enabled, focus_object_name, focus_distance, fstop):
    camera_object = _get_object(camera_name)
    if camera_object is None:
        return _result(False, f"Camera '{camera_name}' was not found.")
    if camera_object.type != "CAMERA":
        return _result(False, f"'{camera_name}' is not a camera.")

    focus_object = None
    if focus_object_name:
        focus_object = _get_object(focus_object_name)
        if focus_object is None:
            return _result(False, f"Focus object '{focus_object_name}' was not found.")

    camera = camera_object.data
    camera.dof.use_dof = bool(enabled)
    camera.dof.aperture_fstop = max(0.1, float(fstop))
    camera.dof.focus_distance = max(0.0, float(focus_distance))
    camera.dof.focus_object = focus_object

    return _result(
        True,
        f"Updated depth of field on {camera_object.name}.",
        enabled=bool(camera.dof.use_dof),
        focus_object=camera.dof.focus_object.name if camera.dof.focus_object else None,
        focus_distance=float(camera.dof.focus_distance),
        fstop=float(camera.dof.aperture_fstop),
    )


def add_tracking_constraint(object_name, target_name, tracking_type, track_axis, up_axis):
    obj = _get_object(object_name)
    target = _get_object(target_name)
    if obj is None:
        return _result(False, f"Object '{object_name}' was not found.")
    if target is None:
        return _result(False, f"Target '{target_name}' was not found.")
    if obj == target:
        return _result(False, "An object cannot track itself.")

    tracking_type = tracking_type.upper()
    track_axis = track_axis.upper()
    up_axis = up_axis.upper()

    if tracking_type not in {"TRACK_TO", "DAMPED_TRACK"}:
        return _result(False, "Tracking type must be TRACK_TO or DAMPED_TRACK.")

    obj.constraints.new(tracking_type)
    constraint = obj.constraints[-1]
    constraint.name = f"GPT Blend {tracking_type}"
    constraint.target = target
    constraint.track_axis = track_axis

    if tracking_type == "TRACK_TO":
        if up_axis == track_axis:
            obj.constraints.remove(constraint)
            return _result(False, "TRACK_TO requires different track and up axes.")
        constraint.up_axis = up_axis

    return _result(
        True,
        f"Added {tracking_type} constraint to {obj.name} targeting {target.name}.",
        constraint=constraint.name,
        target=target.name,
    )


def add_copy_transforms_constraint(object_name, target_name, mix_mode):
    obj = _get_object(object_name)
    target = _get_object(target_name)
    if obj is None:
        return _result(False, f"Object '{object_name}' was not found.")
    if target is None:
        return _result(False, f"Target '{target_name}' was not found.")
    if obj == target:
        return _result(False, "An object cannot copy transforms from itself.")

    mix_mode = mix_mode.upper()
    allowed = {"REPLACE", "BEFORE_FULL", "BEFORE", "AFTER_FULL", "AFTER"}
    if mix_mode not in allowed:
        return _result(False, f"Unsupported Copy Transforms mix mode: {mix_mode}.")

    constraint = obj.constraints.new("COPY_TRANSFORMS")
    constraint.name = "GPT Blend Copy Transforms"
    constraint.target = target
    constraint.mix_mode = mix_mode

    return _result(
        True,
        f"Added Copy Transforms constraint to {obj.name} using {target.name}.",
        constraint=constraint.name,
        mix_mode=mix_mode,
    )


def remove_constraint(object_name, constraint_name):
    obj = _get_object(object_name)
    if obj is None:
        return _result(False, f"Object '{object_name}' was not found.")
    constraint = obj.constraints.get(constraint_name)
    if constraint is None:
        return _result(False, f"Constraint '{constraint_name}' was not found on {obj.name}.")
    obj.constraints.remove(constraint)
    return _result(True, f"Removed constraint '{constraint_name}' from {obj.name}.")


def set_animation_cycles(object_name, mode_before, mode_after, cycles_before, cycles_after):
    obj = _get_object(object_name)
    if obj is None:
        return _result(False, f"Object '{object_name}' was not found.")
    if not obj.animation_data or not obj.animation_data.action:
        return _result(False, f"Object '{obj.name}' has no animation action.")

    modes = {"NONE", "REPEAT", "REPEAT_OFFSET", "MIRROR"}
    mode_before = mode_before.upper()
    mode_after = mode_after.upper()
    if mode_before not in modes or mode_after not in modes:
        return _result(False, "Animation cycle modes must be NONE, REPEAT, REPEAT_OFFSET, or MIRROR.")

    total = 0
    for fcurve in obj.animation_data.action.fcurves:
        cycles = next((modifier for modifier in fcurve.modifiers if modifier.type == "CYCLES"), None)
        if cycles is None:
            cycles = fcurve.modifiers.new("CYCLES")
        modifiers = list(fcurve.modifiers)
        if cycles not in modifiers:
            return _result(False, f"Could not register a Cycles modifier on {obj.name}.")
        index = modifiers.index(cycles)
        if index != 0:
            # Blender requires Cycles to be the first F-Curve modifier.
            fcurve.modifiers.remove(cycles)
            return _result(
                False,
                f"Cannot safely add Cycles to {obj.name}: an existing F-Curve modifier "
                "would place Cycles after another modifier. Remove/reorder the other "
                "animation modifier first.",
            )

        cycles.mode_before = mode_before
        cycles.mode_after = mode_after
        cycles.cycles_before = max(0, int(cycles_before))
        cycles.cycles_after = max(0, int(cycles_after))
        total += 1

    return _result(
        True,
        f"Configured cyclic animation on {obj.name} across {total} F-curve(s).",
        fcurves_changed=total,
        mode_before=mode_before,
        mode_after=mode_after,
        cycles_before=int(cycles_before),
        cycles_after=int(cycles_after),
    )


def add_scene_marker(name, frame, camera_name):
    scene = bpy.context.scene
    frame = int(frame)
    if frame < scene.frame_start or frame > scene.frame_end:
        return _result(False, "Marker frame must be inside the scene animation range.")

    camera = None
    if camera_name:
        camera = _get_object(camera_name)
        if camera is None or camera.type != "CAMERA":
            return _result(False, f"Camera '{camera_name}' was not found.")

    existing = scene.timeline_markers.get(name)
    if existing:
        existing.frame = frame
        marker = existing
    else:
        marker = scene.timeline_markers.new(name=name, frame=frame)

    marker.camera = camera

    return _result(
        True,
        f"Added timeline marker '{marker.name}' at frame {marker.frame}.",
        name=marker.name,
        frame=marker.frame,
        camera=marker.camera.name if marker.camera else None,
    )


def remove_scene_marker(name):
    scene = bpy.context.scene
    marker = scene.timeline_markers.get(name)
    if marker is None:
        return _result(False, f"Timeline marker '{name}' was not found.")
    scene.timeline_markers.remove(marker)
    return _result(True, f"Removed timeline marker '{name}'.")


def set_render_output(output_path, image_format, film_transparent):
    scene = bpy.context.scene
    allowed_formats = {"PNG", "JPEG", "OPEN_EXR", "OPEN_EXR_MULTILAYER", "TIFF", "BMP", "TARGA"}
    image_format = image_format.upper()
    if image_format not in allowed_formats:
        return _result(False, f"Unsupported image format '{image_format}'.")

    if not output_path:
        return _result(False, "Output path cannot be empty.")

    scene.render.filepath = output_path
    scene.render.image_settings.file_format = image_format
    scene.render.film_transparent = bool(film_transparent)

    return _result(
        True,
        "Updated render output settings.",
        output_path=scene.render.filepath,
        image_format=scene.render.image_settings.file_format,
        film_transparent=bool(scene.render.film_transparent),
    )


TOOL_HANDLERS = {
    "inspect_scene": inspect_scene,
    "create_object": create_object,
    "transform_object": transform_object,
    "rename_object": rename_object,
    "delete_object": delete_object,
    "duplicate_object": duplicate_object,
    "inspect_object": inspect_object,
    "inspect_animation": inspect_animation,
    "select_objects": select_objects,
    "set_material": set_material,
    "set_object_color": set_object_color,
    "add_bevel_modifier": add_bevel_modifier,
    "add_subdivision_modifier": add_subdivision_modifier,
    "remove_modifier": remove_modifier,
    "apply_modifier": apply_modifier,
    "shade_object": shade_object,
    "join_objects": join_objects,
    "set_origin": set_origin,
    "parent_object": parent_object,
    "hide_object": hide_object,
    "set_render_visibility": set_render_visibility,
    "create_collection": create_collection,
    "move_object_to_collection": move_object_to_collection,
    "create_light": create_light,
    "create_camera": create_camera,
    "set_world_background": set_world_background,
    "create_text": create_text,
    "move_object_delta": move_object_delta,
    "rotate_object_delta": rotate_object_delta,
    "set_object_dimensions": set_object_dimensions,
    "apply_object_scale": apply_object_scale,
    "batch_transform_objects": batch_transform_objects,
    "arrange_objects_linear": arrange_objects_linear,
    "align_objects": align_objects,
    "distribute_objects": distribute_objects,
    "create_empty": create_empty,
    "create_bezier_curve": create_bezier_curve,
    "add_array_modifier": add_array_modifier,
    "add_mirror_modifier": add_mirror_modifier,
    "add_solidify_modifier": add_solidify_modifier,
    "add_boolean_modifier": add_boolean_modifier,
    "add_shrinkwrap_modifier": add_shrinkwrap_modifier,
    "add_simple_deform_modifier": add_simple_deform_modifier,
    "add_decimate_modifier": add_decimate_modifier,
    "add_weighted_normal_modifier": add_weighted_normal_modifier,
    "aim_object_at": aim_object_at,
    "set_render_settings": set_render_settings,
    "set_procedural_texture": set_procedural_texture,
    "set_viewport_shading": set_viewport_shading,
    "select_mesh_elements": select_mesh_elements,
    "set_mesh_selection_mode": set_mesh_selection_mode,
    "merge_selected_vertices": merge_selected_vertices,
    "dissolve_selected": dissolve_selected,
    "extrude_selected_faces": extrude_selected_faces,
    "unwrap_uv": unwrap_uv,
    "set_animation_timing": set_animation_timing,
    "animate_object_transform": animate_object_transform,
    "clear_object_animation": clear_object_animation,
    "set_animation_interpolation": set_animation_interpolation,
    "set_camera_depth_of_field": set_camera_depth_of_field,
    "add_tracking_constraint": add_tracking_constraint,
    "add_copy_transforms_constraint": add_copy_transforms_constraint,
    "remove_constraint": remove_constraint,
    "set_animation_cycles": set_animation_cycles,
    "add_scene_marker": add_scene_marker,
    "remove_scene_marker": remove_scene_marker,
    "set_render_output": set_render_output,
}

READ_ONLY_TOOLS = {"inspect_scene", "inspect_object", "inspect_animation"}


def execute_tool(name, arguments):
    handler = TOOL_HANDLERS.get(name)
    if handler is None:
        return _result(False, f"Unknown Blender tool: {name}")

    if name not in READ_ONLY_TOOLS:
        try:
            bpy.ops.ed.undo_push(message=f"GPT Blend: {name}")
        except Exception:
            # Undo checkpoints are helpful but must never prevent a valid tool from running.
            pass

    try:
        return handler(**arguments)
    except Exception as exc:
        return _result(False, f"Tool '{name}' failed: {exc}")
