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
]
