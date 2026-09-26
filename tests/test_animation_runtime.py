import importlib.util
import pathlib
import sys

import bpy


ROOT = pathlib.Path(__file__).resolve().parents[1]
OPS_PATH = ROOT / "gptblend" / "tools" / "blender_ops.py"


def load_ops():
    spec = importlib.util.spec_from_file_location("gptblend_blender_ops_test", OPS_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def check(result, label):
    if not result.get("ok"):
        raise AssertionError(f"{label} failed: {result}")


def main():
    ops = load_ops()

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    obj = bpy.context.object
    obj.name = "GPT Blend Animation Test"

    transform_result = ops.animate_object_transform(
        obj.name,
        [
            {
                "frame": 1,
                "location": [0, 0, 0],
                "rotation_degrees": [0, 0, 0],
                "scale": [1, 1, 1],
                "interpolation": "LINEAR",
            },
            {
                "frame": 20,
                "location": [4, 2, 1],
                "rotation_degrees": [0, 90, 180],
                "scale": [2, 2, 2],
                "interpolation": "BEZIER",
            },
        ],
        True,
    )
    check(transform_result, "transform animation")

    action = obj.animation_data.action
    assert action is not None, "Transform animation did not create an Action."

    curves = ops._action_fcurves(action)
    assert len(curves) == 9, f"Expected 9 transform F-curves, got {len(curves)}"
    key_frames = sorted({round(point.co.x) for curve in curves for point in curve.keyframe_points})
    assert key_frames == [1, 20], f"Unexpected transform keyframes: {key_frames}"

    scene.frame_set(20)
    assert abs(obj.location.x - 4.0) < 1e-5
    assert abs(obj.location.y - 2.0) < 1e-5
    assert abs(obj.location.z - 1.0) < 1e-5
    assert abs(obj.scale.x - 2.0) < 1e-5

    inspect_result = ops.inspect_animation(obj.name)
    check(inspect_result, "animation inspection")
    assert inspect_result["animated"] is True
    assert inspect_result["keyframe_count"] == 18, (
        f"Expected 18 transform keyframe points, got {inspect_result['keyframe_count']}"
    )

    visibility_result = ops.animate_object_visibility(
        obj.name,
        [
            {"frame": 1, "hide_viewport": False, "hide_render": False},
            {"frame": 20, "hide_viewport": True, "hide_render": True},
        ],
        False,
    )
    check(visibility_result, "visibility animation")

    curves = ops._action_fcurves(obj.animation_data.action)
    visibility_curves = [
        curve for curve in curves
        if curve.data_path in {"hide_viewport", "hide_render"}
    ]
    assert len(visibility_curves) == 2, (
        f"Expected 2 visibility F-curves, got {len(visibility_curves)}"
    )
    assert all(
        len(curve.keyframe_points) == 2 for curve in visibility_curves
    )

    scene.frame_set(1)
    assert obj.hide_viewport is False
    assert obj.hide_render is False

    scene.frame_set(20)
    assert obj.hide_viewport is True
    assert obj.hide_render is True

    clear_result = ops.clear_object_animation(obj.name)
    check(clear_result, "clear animation")
    assert obj.animation_data is None, "Animation data was not cleared."

    print("GPT Blend Blender animation runtime test PASSED.")


if __name__ == "__main__":
    main()
