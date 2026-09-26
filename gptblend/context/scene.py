import bpy
import json


def get_scene_context():
    scene = bpy.context.scene

    selected = []
    for obj in bpy.context.selected_objects:
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
        "object_count": len(scene.objects),
        "collections": [c.name for c in bpy.data.collections],
        "world": scene.world.name if scene.world else None,
    }, indent=2)
