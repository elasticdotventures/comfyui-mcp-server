"""
ComfyUI MCP Server - Blender Addon
A Blender addon that integrates with ComfyUI MCP server for generative robotics.
"""

bl_info = {
    "name": "ComfyUI MCP Server",
    "author": "elasticdotventures",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "3D Viewport > Sidebar > ComfyUI MCP",
    "description": "Generate robotics components using ComfyUI and export to URDF",
    "category": "Object",
    "support": "COMMUNITY",
    "doc_url": "https://github.com/elasticdotventures/comfyui-mcp-server",
    "tracker_url": "https://github.com/elasticdotventures/comfyui-mcp-server/issues",
}

import bpy
from . import operators, panels, utils


classes = [
    # Operators
    operators.COMFYUI_OT_generate_component,
    operators.COMFYUI_OT_connect_server,
    operators.COMFYUI_OT_export_urdf,
    
    # Panels
    panels.COMFYUI_PT_main_panel,
    panels.COMFYUI_PT_generation_panel,
    panels.COMFYUI_PT_robotics_panel,
    
    # Properties
    utils.ComfyUIMCPProperties,
]


def register():
    """Register addon classes and properties."""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Add properties to scene
    bpy.types.Scene.comfyui_mcp = bpy.props.PointerProperty(type=utils.ComfyUIMCPProperties)
    
    print("ComfyUI MCP Server addon registered")


def unregister():
    """Unregister addon classes and properties."""
    # Remove properties
    if hasattr(bpy.types.Scene, 'comfyui_mcp'):
        del bpy.types.Scene.comfyui_mcp
    
    # Unregister classes in reverse order
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
    
    print("ComfyUI MCP Server addon unregistered")


if __name__ == "__main__":
    register()