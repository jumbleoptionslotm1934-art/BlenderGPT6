import bpy
import json

def get_scene_context():
    scene = bpy.context.scene
    selected = []
    for obj in bpy.context.selected_objects:
        selected.append({
            "name": obj.name,
            "type": obj.type,
            "location": [round(v, 4) for v in obj.location],
            "rotation": [round(v, 4) for v in obj.rotation_euler],
            "scale": [round(v, 4) for v in obj.scale],
        })
    return json.dumps({
        "scene": scene.name,
        "mode": bpy.context.mode,
        "active_object": bpy.context.active_object.name if bpy.context.active_object else None,
        "selected_objects": selected,
        "object_count": len(scene.objects),
    }, indent=2)
