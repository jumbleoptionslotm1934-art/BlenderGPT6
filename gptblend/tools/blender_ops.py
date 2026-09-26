import bpy
import math

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

def inspect_scene():
    scene = bpy.context.scene
    objects = [{
        "name": o.name, "type": o.type,
        "location": [round(v, 4) for v in o.location],
        "rotation_degrees": [round(math.degrees(v), 2) for v in o.rotation_euler],
        "scale": [round(v, 4) for v in o.scale],
        "selected": o.select_get(),
    } for o in scene.objects]
    return _result(True, "Scene inspected.", scene=scene.name, mode=bpy.context.mode,
                   active_object=bpy.context.active_object.name if bpy.context.active_object else None,
                   objects=objects)

def create_object(object_type, name, location, scale):
    object_type = object_type.upper()
    if object_type not in ALLOWED_PRIMITIVES:
        return _result(False, f"Unsupported primitive: {object_type}")
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
    obj = bpy.data.objects.get(name)
    if obj is None:
        return _result(False, f"Object '{name}' was not found.")
    obj.location = location
    obj.rotation_euler = [math.radians(v) for v in rotation_degrees]
    obj.scale = scale
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    return _result(True, f"Transformed {obj.name}.", name=obj.name)

def rename_object(current_name, new_name):
    obj = bpy.data.objects.get(current_name)
    if obj is None:
        return _result(False, f"Object '{current_name}' was not found.")
    old_name = obj.name
    obj.name = new_name
    return _result(True, f"Renamed {old_name} to {obj.name}.", name=obj.name)

def delete_object(name):
    obj = bpy.data.objects.get(name)
    if obj is None:
        return _result(False, f"Object '{name}' was not found.")
    bpy.data.objects.remove(obj, do_unlink=True)
    return _result(True, f"Deleted {name}.")

def duplicate_object(name, new_name, location):
    source = bpy.data.objects.get(name)
    if source is None:
        return _result(False, f"Object '{name}' was not found.")
    duplicate = source.copy()
    if source.data:
        duplicate.data = source.data.copy()
    duplicate.name = new_name
    duplicate.location = location
    bpy.context.collection.objects.link(duplicate)
    bpy.ops.object.select_all(action="DESELECT")
    duplicate.select_set(True)
    bpy.context.view_layer.objects.active = duplicate
    return _result(True, f"Duplicated {name} as {duplicate.name}.", name=duplicate.name)

TOOL_HANDLERS = {
    "inspect_scene": inspect_scene,
    "create_object": create_object,
    "transform_object": transform_object,
    "rename_object": rename_object,
    "delete_object": delete_object,
    "duplicate_object": duplicate_object,
}

def execute_tool(name, arguments):
    handler = TOOL_HANDLERS.get(name)
    if handler is None:
        return _result(False, f"Unknown Blender tool: {name}")
    try:
        return handler(**arguments)
    except Exception as exc:
        return _result(False, f"Tool '{name}' failed: {exc}")
