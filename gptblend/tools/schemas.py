TOOLS = [
    {
        "type": "function", "name": "inspect_scene",
        "description": "Inspect the current Blender scene, including objects, types, transforms, active object, selection, collections, camera, and mode.",
        "parameters": {"type": "object", "properties": {}, "required": [], "additionalProperties": False},
        "strict": True,
    },
    {
        "type": "function", "name": "create_object",
        "description": "Create a Blender primitive. Supported types: CUBE, UV_SPHERE, CYLINDER, CONE, TORUS, PLANE.",
        "parameters": {
            "type": "object",
            "properties": {
                "object_type": {"type": "string", "enum": ["CUBE", "UV_SPHERE", "CYLINDER", "CONE", "TORUS", "PLANE"]},
                "name": {"type": "string"},
                "location": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                "scale": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
            },
            "required": ["object_type", "name", "location", "scale"], "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "transform_object",
        "description": "Set the location, rotation in degrees, and scale of an existing Blender object.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "location": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                "rotation_degrees": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                "scale": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
            },
            "required": ["name", "location", "rotation_degrees", "scale"], "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "rename_object",
        "description": "Rename an existing Blender object.",
        "parameters": {
            "type": "object",
            "properties": {"current_name": {"type": "string"}, "new_name": {"type": "string"}},
            "required": ["current_name", "new_name"], "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "delete_object",
        "description": "Delete an existing Blender object. Only use when the user explicitly requests deletion.",
        "parameters": {
            "type": "object", "properties": {"name": {"type": "string"}},
            "required": ["name"], "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "duplicate_object",
        "description": "Duplicate an existing Blender object and place the duplicate at a requested location.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"}, "new_name": {"type": "string"},
                "location": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
            },
            "required": ["name", "new_name", "location"], "additionalProperties": False,
        },
        "strict": True,
    },

    # 20 additional Blender capabilities.
    {
        "type": "function", "name": "inspect_object",
        "description": "Inspect one Blender object in detail, including data type, transforms, materials, modifiers, visibility, and parent.",
        "parameters": {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"], "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "select_objects",
        "description": "Select one or more Blender objects by exact name and optionally clear the existing selection.",
        "parameters": {
            "type": "object",
            "properties": {
                "names": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                "clear_existing": {"type": "boolean"},
            },
            "required": ["names", "clear_existing"], "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "set_material",
        "description": "Create or update a material and assign it to a Blender object. Base color is RGBA in the 0-1 range.",
        "parameters": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string"},
                "material_name": {"type": "string"},
                "base_color": {"type": "array", "items": {"type": "number"}, "minItems": 4, "maxItems": 4},
                "metallic": {"type": "number", "minimum": 0, "maximum": 1},
                "roughness": {"type": "number", "minimum": 0, "maximum": 1},
            },
            "required": ["object_name", "material_name", "base_color", "metallic", "roughness"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "set_object_color",
        "description": "Set an object's viewport display color using RGBA values in the 0-1 range.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "color": {"type": "array", "items": {"type": "number"}, "minItems": 4, "maxItems": 4},
            },
            "required": ["name", "color"], "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "add_bevel_modifier",
        "description": "Add a Bevel modifier to an object.",
        "parameters": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string"},
                "modifier_name": {"type": "string"},
                "width": {"type": "number", "minimum": 0},
                "segments": {"type": "integer", "minimum": 1, "maximum": 64},
                "limit_method": {"type": "string", "enum": ["ANGLE", "WEIGHT", "VGROUP", "NONE"]},
            },
            "required": ["object_name", "modifier_name", "width", "segments", "limit_method"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "add_subdivision_modifier",
        "description": "Add a Catmull-Clark subdivision surface modifier.",
        "parameters": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string"},
                "modifier_name": {"type": "string"},
                "levels": {"type": "integer", "minimum": 0, "maximum": 6},
                "render_levels": {"type": "integer", "minimum": 0, "maximum": 6},
            },
            "required": ["object_name", "modifier_name", "levels", "render_levels"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "remove_modifier",
        "description": "Remove a named modifier from an existing object.",
        "parameters": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string"},
                "modifier_name": {"type": "string"},
            },
            "required": ["object_name", "modifier_name"], "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "apply_modifier",
        "description": "Apply a named modifier to an object. Requires Blender Object Mode.",
        "parameters": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string"},
                "modifier_name": {"type": "string"},
            },
            "required": ["object_name", "modifier_name"], "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "shade_object",
        "description": "Set all mesh faces on an object to smooth or flat shading.",
        "parameters": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string"},
                "smooth": {"type": "boolean"},
            },
            "required": ["object_name", "smooth"], "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "join_objects",
        "description": "Join multiple objects of the same Blender object type into one object. Object Mode is required.",
        "parameters": {
            "type": "object",
            "properties": {
                "names": {"type": "array", "items": {"type": "string"}, "minItems": 2},
                "active_name": {"type": "string"},
            },
            "required": ["names", "active_name"], "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "set_origin",
        "description": "Set the origin of an object using Blender's standard origin modes.",
        "parameters": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string"},
                "origin_type": {
                    "type": "string",
                    "enum": ["ORIGIN_GEOMETRY", "ORIGIN_CURSOR", "ORIGIN_CENTER_OF_MASS", "ORIGIN_CENTER_OF_VOLUME"],
                },
            },
            "required": ["object_name", "origin_type"], "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "parent_object",
        "description": "Parent one object to another while preserving the child's current world transform.",
        "parameters": {
            "type": "object",
            "properties": {
                "child_name": {"type": "string"},
                "parent_name": {"type": "string"},
            },
            "required": ["child_name", "parent_name"], "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "hide_object",
        "description": "Hide or unhide an object in the 3D viewport.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "hidden": {"type": "boolean"},
            },
            "required": ["name", "hidden"], "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "set_render_visibility",
        "description": "Enable or disable an object's participation in renders.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "hidden_from_render": {"type": "boolean"},
            },
            "required": ["name", "hidden_from_render"], "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "create_collection",
        "description": "Create a new collection and link it under the scene root or an existing scene collection.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "parent_collection_name": {"type": "string"},
            },
            "required": ["name", "parent_collection_name"], "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "move_object_to_collection",
        "description": "Move an object into an existing collection, unlinking it from its previous collections.",
        "parameters": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string"},
                "collection_name": {"type": "string"},
            },
            "required": ["object_name", "collection_name"], "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "create_light",
        "description": "Create a Blender light with a type, transform, energy, color, and size.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "light_type": {"type": "string", "enum": ["POINT", "AREA", "SUN", "SPOT"]},
                "location": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                "rotation_degrees": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                "energy": {"type": "number", "minimum": 0},
                "color": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                "size": {"type": "number", "minimum": 0.001},
            },
            "required": ["name", "light_type", "location", "rotation_degrees", "energy", "color", "size"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "create_camera",
        "description": "Create a camera with a location, rotation, and lens, and optionally make it the active scene camera.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "location": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                "rotation_degrees": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                "lens": {"type": "number", "minimum": 1, "maximum": 500},
                "make_active": {"type": "boolean"},
            },
            "required": ["name", "location", "rotation_degrees", "lens", "make_active"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "set_world_background",
        "description": "Set the Blender world background color and strength.",
        "parameters": {
            "type": "object",
            "properties": {
                "color": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                "strength": {"type": "number", "minimum": 0},
            },
            "required": ["color", "strength"], "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "create_text",
        "description": "Create a 3D text object with custom body, size, position, rotation, and extrusion.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "body": {"type": "string"},
                "location": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                "rotation_degrees": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                "size": {"type": "number", "minimum": 0.001},
                "extrude": {"type": "number", "minimum": 0},
            },
            "required": ["name", "body", "location", "rotation_degrees", "size", "extrude"],
            "additionalProperties": False,
        },
        "strict": True,
    },
,
    
    # 20 advanced workflow and modeling capabilities.
    {
        "type": "function", "name": "move_object_delta",
        "description": "Move an existing object by a relative XYZ offset in Blender units.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "offset": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
            },
            "required": ["name", "offset"], "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "rotate_object_delta",
        "description": "Rotate an existing object by relative Euler angle deltas in degrees.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "rotation_delta_degrees": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
            },
            "required": ["name", "rotation_delta_degrees"], "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "set_object_dimensions",
        "description": "Set the world-space dimensions of an object in XYZ Blender units.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "dimensions": {"type": "array", "items": {"type": "number", "minimum": 0.0001}, "minItems": 3, "maxItems": 3},
            },
            "required": ["name", "dimensions"], "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "apply_object_scale",
        "description": "Apply an object's current scale to its underlying geometry.",
        "parameters": {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"], "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "batch_transform_objects",
        "description": "Apply the same relative move, relative rotation, and scale multiplier to multiple named objects.",
        "parameters": {
            "type": "object",
            "properties": {
                "names": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                "location_offset": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                "rotation_delta_degrees": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                "scale_multiplier": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
            },
            "required": ["names", "location_offset", "rotation_delta_degrees", "scale_multiplier"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "arrange_objects_linear",
        "description": "Arrange named objects evenly along an axis starting from a specified position.",
        "parameters": {
            "type": "object",
            "properties": {
                "names": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                "axis": {"type": "string", "enum": ["X", "Y", "Z"]},
                "start": {"type": "number"},
                "spacing": {"type": "number"},
                "preserve_other_axes": {"type": "boolean"},
            },
            "required": ["names", "axis", "start", "spacing", "preserve_other_axes"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "align_objects",
        "description": "Align the origins of named objects to a common minimum, maximum, or center position along one axis.",
        "parameters": {
            "type": "object",
            "properties": {
                "names": {"type": "array", "items": {"type": "string"}, "minItems": 2},
                "axis": {"type": "string", "enum": ["X", "Y", "Z"]},
                "mode": {"type": "string", "enum": ["MIN", "MAX", "CENTER"]},
            },
            "required": ["names", "axis", "mode"], "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "distribute_objects",
        "description": "Evenly distribute named objects between the first and last object's current axis positions.",
        "parameters": {
            "type": "object",
            "properties": {
                "names": {"type": "array", "items": {"type": "string"}, "minItems": 3},
                "axis": {"type": "string", "enum": ["X", "Y", "Z"]},
            },
            "required": ["names", "axis"], "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "create_empty",
        "description": "Create a Blender Empty helper object.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "empty_type": {"type": "string", "enum": ["PLAIN_AXES", "ARROWS", "SINGLE_ARROW", "CIRCLE", "CUBE", "SPHERE", "CONE", "IMAGE"]},
                "location": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                "size": {"type": "number", "minimum": 0.001},
            },
            "required": ["name", "empty_type", "location", "size"], "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "create_bezier_curve",
        "description": "Create a 3D Bezier curve object.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "location": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                "scale": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                "bevel_depth": {"type": "number", "minimum": 0},
                "bevel_resolution": {"type": "integer", "minimum": 0, "maximum": 32},
            },
            "required": ["name", "location", "scale", "bevel_depth", "bevel_resolution"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "add_array_modifier",
        "description": "Add an Array modifier with a fixed count and relative X/Y/Z offset.",
        "parameters": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string"},
                "modifier_name": {"type": "string"},
                "count": {"type": "integer", "minimum": 1, "maximum": 1000},
                "relative_offset": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
            },
            "required": ["object_name", "modifier_name", "count", "relative_offset"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "add_mirror_modifier",
        "description": "Add a Mirror modifier using selected X/Y/Z axes.",
        "parameters": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string"},
                "modifier_name": {"type": "string"},
                "use_x": {"type": "boolean"},
                "use_y": {"type": "boolean"},
                "use_z": {"type": "boolean"},
                "use_clip": {"type": "boolean"},
            },
            "required": ["object_name", "modifier_name", "use_x", "use_y", "use_z", "use_clip"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "add_solidify_modifier",
        "description": "Add a Solidify modifier to give a mesh surface thickness.",
        "parameters": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string"},
                "modifier_name": {"type": "string"},
                "thickness": {"type": "number"},
                "offset": {"type": "number", "minimum": -1, "maximum": 1},
            },
            "required": ["object_name", "modifier_name", "thickness", "offset"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "add_boolean_modifier",
        "description": "Add a Boolean modifier using another mesh object as the operand.",
        "parameters": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string"},
                "modifier_name": {"type": "string"},
                "operand_name": {"type": "string"},
                "operation": {"type": "string", "enum": ["UNION", "INTERSECT", "DIFFERENCE"]},
            },
            "required": ["object_name", "modifier_name", "operand_name", "operation"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "add_shrinkwrap_modifier",
        "description": "Add a Shrinkwrap modifier that conforms a mesh to a target object.",
        "parameters": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string"},
                "modifier_name": {"type": "string"},
                "target_name": {"type": "string"},
                "offset": {"type": "number"},
            },
            "required": ["object_name", "modifier_name", "target_name", "offset"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "add_simple_deform_modifier",
        "description": "Add a Simple Deform modifier for twist, bend, taper, or stretch.",
        "parameters": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string"},
                "modifier_name": {"type": "string"},
                "deform_method": {"type": "string", "enum": ["TWIST", "BEND", "TAPER", "STRETCH"]},
                "deform_axis": {"type": "string", "enum": ["X", "Y", "Z"]},
                "angle_degrees": {"type": "number"},
            },
            "required": ["object_name", "modifier_name", "deform_method", "deform_axis", "angle_degrees"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "add_decimate_modifier",
        "description": "Add a Decimate modifier to reduce mesh geometry by a ratio.",
        "parameters": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string"},
                "modifier_name": {"type": "string"},
                "ratio": {"type": "number", "minimum": 0.01, "maximum": 1},
            },
            "required": ["object_name", "modifier_name", "ratio"], "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "add_weighted_normal_modifier",
        "description": "Add a Weighted Normal modifier to improve hard-surface shading.",
        "parameters": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string"},
                "modifier_name": {"type": "string"},
                "keep_sharp": {"type": "boolean"},
            },
            "required": ["object_name", "modifier_name", "keep_sharp"], "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "aim_object_at",
        "description": "Rotate an object so its local -Z axis points toward another object while keeping local Y as the up direction.",
        "parameters": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string"},
                "target_name": {"type": "string"},
            },
            "required": ["object_name", "target_name"], "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function", "name": "set_render_settings",
        "description": "Configure scene render engine, resolution, resolution percentage, and frame rate.",
        "parameters": {
            "type": "object",
            "properties": {
                "engine": {"type": "string", "enum": ["BLENDER_EEVEE_NEXT", "BLENDER_WORKBENCH", "CYCLES"]},
                "resolution_x": {"type": "integer", "minimum": 16, "maximum": 16384},
                "resolution_y": {"type": "integer", "minimum": 16, "maximum": 16384},
                "resolution_percentage": {"type": "integer", "minimum": 1, "maximum": 100},
                "fps": {"type": "number", "minimum": 1, "maximum": 240},
            },
            "required": ["engine", "resolution_x", "resolution_y", "resolution_percentage", "fps"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]