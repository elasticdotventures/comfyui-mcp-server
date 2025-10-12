"""
Blender operators for ComfyUI MCP integration.
"""

import bpy
import bmesh
from bpy.types import Operator
from bpy.props import StringProperty
import asyncio
import threading
import json
from .mcp_client import MCPClient
from .utils import validate_robot_assembly, create_joint_constraint


class COMFYUI_OT_connect_server(Operator):
    """Connect to ComfyUI MCP Server"""
    bl_idname = "comfyui.connect_server"
    bl_label = "Connect to MCP Server"
    bl_description = "Connect to the ComfyUI MCP server"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.scene.comfyui_mcp
        
        try:
            # Test connection
            client = MCPClient(props.server_host, props.server_port)
            if client.test_connection():
                props.connected = True
                self.report({'INFO'}, f"Connected to MCP server at {props.server_host}:{props.server_port}")
            else:
                props.connected = False
                self.report({'ERROR'}, "Failed to connect to MCP server")
        except Exception as e:
            props.connected = False
            self.report({'ERROR'}, f"Connection error: {str(e)}")
        
        return {'FINISHED'}


class COMFYUI_OT_generate_component(Operator):
    """Generate robot component using ComfyUI"""
    bl_idname = "comfyui.generate_component"
    bl_label = "Generate Component"
    bl_description = "Generate a robot component using ComfyUI MCP server"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.comfyui_mcp
        
        if not props.connected:
            self.report({'ERROR'}, "Not connected to MCP server. Connect first.")
            return {'CANCELLED'}
        
        try:
            # Prepare generation parameters
            params = {
                "prompt": f"{props.component_type}: {props.prompt}",
                "seed": props.seed,
                "steps": props.steps,
                "cfg": props.cfg,
                "denoise": props.denoise
            }
            
            # Start generation in separate thread
            self.generate_async(context, params)
            
            self.report({'INFO'}, "Component generation started...")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Generation failed: {str(e)}")
            return {'CANCELLED'}
    
    def generate_async(self, context, params):
        """Run generation in separate thread."""
        def run_generation():
            try:
                props = context.scene.comfyui_mcp
                client = MCPClient(props.server_host, props.server_port)
                
                # Call MCP server
                result = client.text_to_image(**params)
                
                # Schedule Blender update in main thread
                def update_blender():
                    self.create_component_from_result(context, result)
                
                bpy.app.timers.register(update_blender, first_interval=0.1)
                
            except Exception as e:
                def show_error():
                    self.report({'ERROR'}, f"Generation error: {str(e)}")
                bpy.app.timers.register(show_error, first_interval=0.1)
        
        thread = threading.Thread(target=run_generation)
        thread.daemon = True
        thread.start()
    
    def create_component_from_result(self, context, result):
        """Create Blender object from generation result."""
        try:
            # For now, create a placeholder mesh
            # In full implementation, this would process the ComfyUI output
            # and create actual geometry
            
            bpy.ops.mesh.primitive_cube_add()
            obj = context.active_object
            obj.name = f"Generated_{context.scene.comfyui_mcp.component_type}"
            
            # Add custom properties
            obj["comfyui_generated"] = True
            obj["component_type"] = context.scene.comfyui_mcp.component_type
            obj["generation_prompt"] = context.scene.comfyui_mcp.prompt
            
            self.report({'INFO'}, f"Generated component: {obj.name}")
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to create component: {str(e)}")


class COMFYUI_OT_add_joint(Operator):
    """Add a joint definition"""
    bl_idname = "comfyui.add_joint"
    bl_label = "Add Joint"
    bl_description = "Add a new joint to the robot definition"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.comfyui_mcp
        
        # Add new joint
        joint = props.joints.add()
        joint.name = f"joint_{len(props.joints)}"
        
        # Set as active joint
        props.joint_index = len(props.joints) - 1
        
        self.report({'INFO'}, f"Added joint: {joint.name}")
        return {'FINISHED'}


class COMFYUI_OT_remove_joint(Operator):
    """Remove a joint definition"""
    bl_idname = "comfyui.remove_joint"
    bl_label = "Remove Joint"
    bl_description = "Remove the active joint from the robot definition"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.comfyui_mcp
        
        if props.joints and 0 <= props.joint_index < len(props.joints):
            joint_name = props.joints[props.joint_index].name
            props.joints.remove(props.joint_index)
            
            # Adjust active index
            if props.joint_index >= len(props.joints) and props.joints:
                props.joint_index = len(props.joints) - 1
            
            self.report({'INFO'}, f"Removed joint: {joint_name}")
        else:
            self.report({'WARNING'}, "No joint to remove")
        
        return {'FINISHED'}


class COMFYUI_OT_create_joint_constraint(Operator):
    """Create Blender constraint for selected joint"""
    bl_idname = "comfyui.create_joint_constraint"
    bl_label = "Create Joint Constraint"
    bl_description = "Create Blender constraint representing the robot joint"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.comfyui_mcp
        selected = context.selected_objects
        
        if len(selected) < 2:
            self.report({'ERROR'}, "Select at least 2 objects to create joint")
            return {'CANCELLED'}
        
        if not props.joints or props.joint_index >= len(props.joints):
            self.report({'ERROR'}, "No active joint defined")
            return {'CANCELLED'}
        
        joint = props.joints[props.joint_index]
        obj1, obj2 = selected[0], selected[1]
        
        constraint = create_joint_constraint(
            obj1, obj2, joint.joint_type, 
            axis=(joint.axis_x, joint.axis_y, joint.axis_z)
        )
        
        if constraint:
            self.report({'INFO'}, f"Created {joint.joint_type} constraint between {obj1.name} and {obj2.name}")
        else:
            self.report({'ERROR'}, "Failed to create constraint")
        
        return {'FINISHED'}


class COMFYUI_OT_export_urdf(Operator):
    """Export robot assembly to URDF"""
    bl_idname = "comfyui.export_urdf"
    bl_label = "Export URDF"
    bl_description = "Export the robot assembly to URDF format"
    bl_options = {'REGISTER'}
    
    filepath: StringProperty(
        name="File Path",
        description="Path for URDF export",
        subtype='FILE_PATH',
    )
    
    def invoke(self, context, event):
        props = context.scene.comfyui_mcp
        self.filepath = props.export_path + props.robot_name + ".urdf"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        props = context.scene.comfyui_mcp
        
        # Validate assembly
        errors, warnings = validate_robot_assembly(context)
        
        if errors:
            self.report({'ERROR'}, f"Export failed: {'; '.join(errors)}")
            return {'CANCELLED'}
        
        if warnings:
            for warning in warnings:
                self.report({'WARNING'}, warning)
        
        try:
            # Export URDF
            self.export_urdf_file(context, self.filepath)
            self.report({'INFO'}, f"URDF exported to: {self.filepath}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Export failed: {str(e)}")
            return {'CANCELLED'}
    
    def export_urdf_file(self, context, filepath):
        """Export URDF file with current robot assembly."""
        props = context.scene.comfyui_mcp
        selected = context.selected_objects
        
        # Generate basic URDF structure
        urdf_content = self.generate_urdf_xml(props, selected)
        
        # Write URDF file
        with open(filepath, 'w') as f:
            f.write(urdf_content)
        
        # Export meshes if requested
        if props.include_meshes:
            self.export_meshes(selected, filepath, props.mesh_format)
    
    def generate_urdf_xml(self, props, objects):
        """Generate URDF XML content."""
        # Basic URDF template - this would be much more sophisticated in practice
        urdf = f'''<?xml version="1.0"?>
<robot name="{props.robot_name}">
'''
        
        # Add base link
        urdf += '''  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.1 0.1 0.1"/>
      </geometry>
    </visual>
    <collision>
      <geometry>
        <box size="0.1 0.1 0.1"/>
      </geometry>
    </collision>
  </link>
'''
        
        # Add objects as links
        for i, obj in enumerate(objects):
            if obj.type == 'MESH':
                urdf += f'''  <link name="{obj.name}">
    <visual>
      <geometry>
        <mesh filename="meshes/{obj.name}.{props.mesh_format.lower()}"/>
      </geometry>
    </visual>
    <collision>
      <geometry>
        <mesh filename="meshes/{obj.name}.{props.mesh_format.lower()}"/>
      </geometry>
    </collision>
  </link>
'''
        
        # Add joints
        for joint in props.joints:
            urdf += f'''  <joint name="{joint.name}" type="{joint.joint_type}">
    <parent link="base_link"/>
    <child link="link_{joint.name}"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <axis xyz="{joint.axis_x} {joint.axis_y} {joint.axis_z}"/>
    <limit lower="{joint.limit_lower}" upper="{joint.limit_upper}" effort="{joint.max_effort}" velocity="{joint.max_velocity}"/>
  </joint>
'''
        
        urdf += '</robot>'
        return urdf
    
    def export_meshes(self, objects, urdf_path, mesh_format):
        """Export mesh files for URDF."""
        import os
        
        # Create meshes directory
        urdf_dir = os.path.dirname(urdf_path)
        mesh_dir = os.path.join(urdf_dir, "meshes")
        os.makedirs(mesh_dir, exist_ok=True)
        
        # Export each mesh object
        for obj in objects:
            if obj.type == 'MESH':
                mesh_path = os.path.join(mesh_dir, f"{obj.name}.{mesh_format.lower()}")
                
                # Select only this object
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                
                # Export based on format
                if mesh_format == 'STL':
                    bpy.ops.export_mesh.stl(filepath=mesh_path, use_selection=True)
                elif mesh_format == 'OBJ':
                    bpy.ops.export_scene.obj(filepath=mesh_path, use_selection=True)
                elif mesh_format == 'DAE':
                    bpy.ops.wm.collada_export(filepath=mesh_path, selected=True)