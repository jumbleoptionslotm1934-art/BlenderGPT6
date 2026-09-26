import bpy
import json


def _scene_collection_names(scene):
    names = [scene.collection.name]
    stack = list(scene.collection.children)
    visited = set()

    while stack:
        collection = stack.pop()
        key = collection.as_pointer()
        if key in visited:
            continue
        visited.add(key)
        names.append(collection.name)
        stack.extend(collection.children)

    return names


def get_scene_context():
    scene = bpy.context.scene

    selected = []
    selected_objects = list(bpy.context.selected_objects)[:100]
    for obj in selected_objects:
        materials = []
        if hasattr(obj.data, "materials"):
            materials = [m.name if m else None for m in obj.data.materials]

        modifiers = [
            {
                "name": modifier.name,
                "type": modifier.type,
                "show_viewport": modifier.show_viewport,
                "show_render": modifier.show_render,
            }
            for modifier in obj.modifiers
        ]

        selected.append({
            "name": obj.name,
            "type": obj.type,
            "location": [round(v, 4) for v in obj.location],
            "rotation_degrees": [round(v, 2) for v in obj.rotation_euler],
            "scale": [round(v, 4) for v in obj.scale],
            "dimensions": [round(v, 4) for v in obj.dimensions],
            "hidden": obj.hide_get(),
            "hidden_from_render": obj.hide_render,
            "collections": [c.name for c in obj.users_collection],
            "materials": materials,
            "modifiers": modifiers,
        })

    return json.dumps({
        "scene": scene.name,
        "mode": bpy.context.mode,
        "active_object": bpy.context.active_object.name if bpy.context.active_object else None,
        "active_camera": scene.camera.name if scene.camera else None,
        "selected_objects": selected,
        "selected_objects_returned": len(selected),
        "selected_objects_truncated": len(bpy.context.selected_objects) > len(selected),
        "object_count": len(scene.objects),
        "collections": _scene_collection_names(scene),
        "world": scene.world.name if scene.world else None,
        "world_background": (
            {
                "color": list(scene.world.node_tree.nodes["Background"].inputs["Color"].default_value[:3]),
                "strength": float(scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value),
            }
            if scene.world and scene.world.use_nodes and scene.world.node_tree.nodes.get("Background")
            else None
        ),
        "animation": {
            "fps": float(scene.render.fps),
            "start_frame": scene.frame_start,
            "end_frame": scene.frame_end,
            "current_frame": scene.frame_current,
        },
        "render": {
            "engine": scene.render.engine,
            "resolution": [scene.render.resolution_x, scene.render.resolution_y],
            "resolution_percentage": scene.render.resolution_percentage,
            "image_format": scene.render.image_settings.file_format,
            "output_path": scene.render.filepath,
            "film_transparent": bool(scene.render.film_transparent),
        },
        "units": {
            "system": scene.unit_settings.system,
            "length_unit": scene.unit_settings.length_unit,
            "scale_length": float(scene.unit_settings.scale_length),
        },
    }, indent=2)
