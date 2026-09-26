import ast
import pathlib
import re
import tomllib


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "gptblend" / "tools" / "schemas.py"
OPS = ROOT / "gptblend" / "tools" / "blender_ops.py"
MANIFEST = ROOT / "gptblend" / "blender_manifest.toml"
README = ROOT / "README.md"


def _assignment(tree, name):
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return node.value
    raise AssertionError(f"Could not find assignment: {name}")


def _literal(value):
    return ast.literal_eval(value)


def main():
    schemas_tree = ast.parse(SCHEMAS.read_text(encoding="utf-8"))
    ops_tree = ast.parse(OPS.read_text(encoding="utf-8"))

    tools_value = _literal(_assignment(schemas_tree, "TOOLS"))
    schema_names = [tool["name"] for tool in tools_value]
    if len(schema_names) != len(set(schema_names)):
        raise AssertionError("Duplicate tool schema names found.")

    handlers_node = _assignment(ops_tree, "TOOL_HANDLERS")
    if not isinstance(handlers_node, ast.Dict):
        raise AssertionError("TOOL_HANDLERS must be a dict literal.")
    handler_names = [
        ast.literal_eval(key)
        for key in handlers_node.keys
        if isinstance(key, ast.Constant) and isinstance(key.value, str)
    ]

    missing = sorted(set(schema_names) - set(handler_names))
    extra = sorted(set(handler_names) - set(schema_names))
    if missing:
        raise AssertionError(f"Missing handlers: {missing}")
    if extra:
        raise AssertionError(f"Extra handlers: {extra}")

    for name in schema_names:
        if not re.search(rf"^def {re.escape(name)}\(", OPS.read_text(encoding="utf-8"), re.MULTILINE):
            raise AssertionError(f"Handler function is missing: {name}")

    manifest = tomllib.loads(MANIFEST.read_text(encoding="utf-8"))
    version = manifest["version"]
    readme = README.read_text(encoding="utf-8")
    if f"GPT Blend {version}" not in readme:
        raise AssertionError("README version does not match manifest version.")
    if f"{len(schema_names)} model-facing Blender tools" not in readme:
        raise AssertionError("README tool count does not match schemas.py.")

    print(f"GPT Blend validation passed: {len(schema_names)} tools, {len(handler_names)} handlers, version {version}.")


if __name__ == "__main__":
    main()
