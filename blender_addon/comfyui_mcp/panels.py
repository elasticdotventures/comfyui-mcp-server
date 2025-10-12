"""
Blender UI panels for ComfyUI MCP integration.
"""

import bpy
from bpy.types import Panel
from .utils import get_active_joint


class COMFYUI_PT_main_panel(Panel):
    """Main ComfyUI MCP panel in 3D viewport sidebar."""
    bl_label = "ComfyUI MCP Server"
    bl_idname = "COMFYUI_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ComfyUI MCP"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.comfyui_mcp
        
        # Connection section
        box = layout.box()
        box.label(text="Server Connection", icon='WORLD')
        
        col = box.column(align=True)
        col.prop(props, "server_host")
        col.prop(props, "server_port")
        
        if props.connected:
            col.operator("comfyui.connect_server", text="Reconnect", icon='FILE_REFRESH')
            col.label(text="Status: Connected", icon='CHECKMARK')
        else:
            col.operator("comfyui.connect_server", text="Connect", icon='PLUGIN')
            col.label(text="Status: Disconnected", icon='ERROR')


class COMFYUI_PT_generation_panel(Panel):
    """Panel for component generation."""
    bl_label = "Generate Components"
    bl_idname = "COMFYUI_PT_generation_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ComfyUI MCP"
    bl_parent_id = "COMFYUI_PT_main_panel"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.comfyui_mcp
        
        # Generation parameters
        box = layout.box()
        box.label(text="Generation Parameters", icon='MODIFIER')
        
        col = box.column(align=True)
        col.prop(props, "component_type")
        col.prop(props, "prompt")
        
        # Advanced parameters in sub-box
        sub_box = box.box()
        sub_box.label(text="Advanced Settings")
        sub_col = sub_box.column(align=True)
        sub_col.prop(props, "seed")
        sub_col.prop(props, "steps")
        sub_col.prop(props, "cfg")
        sub_col.prop(props, "denoise")
        
        # Generation button
        col = layout.column()
        col.scale_y = 1.5
        if props.connected:
            col.operator("comfyui.generate_component", text="Generate Component", icon='ADD')
        else:
            col.enabled = False
            col.operator("comfyui.generate_component", text="Connect First", icon='ERROR')


class COMFYUI_PT_robotics_panel(Panel):
    """Panel for robotics assembly and URDF export."""
    bl_label = "Robotics Assembly"
    bl_idname = "COMFYUI_PT_robotics_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ComfyUI MCP"
    bl_parent_id = "COMFYUI_PT_main_panel"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.comfyui_mcp
        
        # Robot definition
        box = layout.box()
        box.label(text="Robot Definition", icon='ARMATURE_DATA')
        box.prop(props, "robot_name")
        
        # Joints section
        joints_box = layout.box()
        joints_box.label(text="Joints", icon='CONSTRAINT')
        
        # Joint list and controls
        row = joints_box.row()
        row.operator("comfyui.add_joint", text="Add", icon='ADD')
        row.operator("comfyui.remove_joint", text="Remove", icon='REMOVE')
        
        if props.joints:
            # Joint selection
            joints_box.prop(props, "joint_index", text="Active Joint")
            
            # Active joint properties
            active_joint = get_active_joint(context)
            if active_joint:
                joint_box = joints_box.box()
                joint_box.label(text=f"Joint: {active_joint.name}")
                
                col = joint_box.column(align=True)
                col.prop(active_joint, "name")
                col.prop(active_joint, "joint_type")
                
                # Axis settings
                if active_joint.joint_type in ['revolute', 'prismatic', 'continuous']:
                    axis_row = col.row(align=True)
                    axis_row.label(text="Axis:")
                    axis_row.prop(active_joint, "axis_x", text="X")
                    axis_row.prop(active_joint, "axis_y", text="Y")
                    axis_row.prop(active_joint, "axis_z", text="Z")
                
                # Limits
                if active_joint.joint_type in ['revolute', 'prismatic']:
                    col.separator()
                    col.label(text="Limits:")
                    limit_col = col.column(align=True)
                    limit_col.prop(active_joint, "limit_lower")
                    limit_col.prop(active_joint, "limit_upper")
                    limit_col.prop(active_joint, "max_effort")
                    limit_col.prop(active_joint, "max_velocity")
                
                # Create constraint button
                joints_box.operator("comfyui.create_joint_constraint", 
                                  text="Create Constraint", icon='CONSTRAINT')
        
        # Export section
        export_box = layout.box()
        export_box.label(text="URDF Export", icon='EXPORT')
        
        col = export_box.column(align=True)
        col.prop(props, "export_path")
        col.prop(props, "include_meshes")
        
        if props.include_meshes:
            col.prop(props, "mesh_format")
        
        # Export button
        col = export_box.column()
        col.scale_y = 1.5
        
        selected_count = len(context.selected_objects)
        if selected_count > 0:
            col.operator("comfyui.export_urdf", 
                        text=f"Export URDF ({selected_count} objects)", 
                        icon='EXPORT')
        else:
            col.enabled = False
            col.operator("comfyui.export_urdf", 
                        text="Select Objects First", 
                        icon='ERROR')


class COMFYUI_PT_tools_panel(Panel):
    """Additional tools panel."""
    bl_label = "Tools"
    bl_idname = "COMFYUI_PT_tools_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ComfyUI MCP"
    bl_parent_id = "COMFYUI_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        # Utility tools
        box = layout.box()
        box.label(text="Utilities", icon='TOOL_SETTINGS')
        
        col = box.column(align=True)
        col.operator("object.origin_set", text="Origin to Geometry").type = 'ORIGIN_GEOMETRY'
        col.operator("object.transform_apply", text="Apply Transform").location = True
        
        # Robotics helpers
        robotics_box = layout.box()
        robotics_box.label(text="Robotics Helpers", icon='ARMATURE_DATA')
        
        col = robotics_box.column(align=True)
        col.operator("mesh.primitive_cylinder_add", text="Add Cylinder (Joint)")
        col.operator("mesh.primitive_cube_add", text="Add Cube (Link)")
        
        # Generation info
        info_box = layout.box()
        info_box.label(text="Generated Objects", icon='INFO')
        
        generated_objects = [obj for obj in context.scene.objects 
                           if obj.get("comfyui_generated", False)]
        
        if generated_objects:
            for obj in generated_objects[:5]:  # Show first 5
                row = info_box.row()
                row.label(text=obj.name, icon='OBJECT_DATA')
                row.prop(obj, "select", text="")
            
            if len(generated_objects) > 5:
                info_box.label(text=f"... and {len(generated_objects) - 5} more")
        else:
            info_box.label(text="No generated objects", icon='ERROR')