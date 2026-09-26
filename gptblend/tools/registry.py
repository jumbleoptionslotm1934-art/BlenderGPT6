from .schemas import TOOLS
from .blender_ops import execute_tool

def get_tools():
    return TOOLS

def run_tool(name, arguments):
    return execute_tool(name, arguments)
