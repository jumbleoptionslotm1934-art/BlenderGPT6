TOOLS = [
    {
        "type": "function", "name": "inspect_scene",
        "description": "Inspect the current Blender scene, including objects, types, transforms, active object, selection, and mode.",
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
]
