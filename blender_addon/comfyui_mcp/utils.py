"""
Utility classes and functions for ComfyUI MCP Blender integration.
"""

import bpy
from bpy.props import (
    StringProperty, 
    IntProperty, 
    FloatProperty, 
    BoolProperty, 
    EnumProperty,
    CollectionProperty
)
from bpy.types import PropertyGroup


class ComfyUIJointProperty(PropertyGroup):
    """Properties for robot joints."""
    
    name: StringProperty(
        name="Joint Name",
        description="Name of the joint",
        default="joint"
    )
    
    joint_type: EnumProperty(
        name="Joint Type",
        description="Type of joint",
        items=[
            ('revolute', 'Revolute', 'Revolute joint (rotational)'),
            ('prismatic', 'Prismatic', 'Prismatic joint (linear)'),
            ('fixed', 'Fixed', 'Fixed joint (no motion)'),
            ('continuous', 'Continuous', 'Continuous joint (unlimited rotation)'),
            ('planar', 'Planar', 'Planar joint (2D motion)'),
            ('floating', 'Floating', 'Floating joint (6DOF)'),
        ],
        default='revolute'
    )
    
    axis_x: FloatProperty(name="Axis X", default=1.0, min=-1.0, max=1.0)
    axis_y: FloatProperty(name="Axis Y", default=0.0, min=-1.0, max=1.0)
    axis_z: FloatProperty(name="Axis Z", default=0.0, min=-1.0, max=1.0)
    
    limit_lower: FloatProperty(
        name="Lower Limit",
        description="Lower joint limit (radians for revolute, meters for prismatic)",
        default=-3.14159
    )
    
    limit_upper: FloatProperty(
        name="Upper Limit", 
        description="Upper joint limit (radians for revolute, meters for prismatic)",
        default=3.14159
    )
    
    max_effort: FloatProperty(
        name="Max Effort",
        description="Maximum effort (torque/force)",
        default=100.0
    )
    
    max_velocity: FloatProperty(
        name="Max Velocity",
        description="Maximum velocity (rad/s or m/s)",
        default=1.0
    )


class ComfyUIMCPProperties(PropertyGroup):
    """Main property group for ComfyUI MCP addon."""
    
    # Server connection
    server_host: StringProperty(
        name="Server Host",
        description="ComfyUI MCP server host",
        default="localhost"
    )
    
    server_port: IntProperty(
        name="Server Port",
        description="ComfyUI MCP server port",
        default=9000,
        min=1,
        max=65535
    )
    
    connected: BoolProperty(
        name="Connected",
        description="Connection status to MCP server",
        default=False
    )
    
    # Generation parameters
    prompt: StringProperty(
        name="Prompt",
        description="Description of the component to generate",
        default="robot arm joint"
    )
    
    component_type: EnumProperty(
        name="Component Type",
        description="Type of robot component to generate",
        items=[
            ('joint', 'Joint', 'Robot joint component'),
            ('link', 'Link', 'Robot link component'),
            ('gripper', 'Gripper', 'End effector gripper'),
            ('sensor', 'Sensor', 'Sensor housing'),
            ('frame', 'Frame', 'Structural frame'),
            ('custom', 'Custom', 'Custom component'),
        ],
        default='joint'
    )
    
    seed: IntProperty(
        name="Seed",
        description="Random seed for generation",
        default=42
    )
    
    steps: IntProperty(
        name="Steps",
        description="Number of generation steps",
        default=20,
        min=1,
        max=100
    )
    
    cfg: FloatProperty(
        name="CFG Scale",
        description="Classifier-free guidance scale",
        default=8.0,
        min=1.0,
        max=20.0
    )
    
    denoise: FloatProperty(
        name="Denoise",
        description="Denoising strength",
        default=1.0,
        min=0.0,
        max=1.0
    )
    
    # Robot assembly properties
    robot_name: StringProperty(
        name="Robot Name",
        description="Name for the robot assembly",
        default="generated_robot"
    )
    
    joints: CollectionProperty(
        type=ComfyUIJointProperty,
        name="Joints",
        description="Robot joints collection"
    )
    
    joint_index: IntProperty(
        name="Joint Index",
        description="Active joint index",
        default=0
    )
    
    # Export settings
    export_path: StringProperty(
        name="Export Path",
        description="Path for URDF export",
        default="//robot_export/",
        subtype='DIR_PATH'
    )
    
    include_meshes: BoolProperty(
        name="Include Meshes",
        description="Export mesh files with URDF",
        default=True
    )
    
    mesh_format: EnumProperty(
        name="Mesh Format",
        description="Format for exported meshes",
        items=[
            ('STL', 'STL', 'STL format'),
            ('OBJ', 'OBJ', 'OBJ format'),
            ('DAE', 'Collada', 'Collada DAE format'),
        ],
        default='STL'
    )


def get_active_joint(context):
    """Get the currently active joint property."""
    props = context.scene.comfyui_mcp
    if props.joints and 0 <= props.joint_index < len(props.joints):
        return props.joints[props.joint_index]
    return None


def create_joint_constraint(obj1, obj2, joint_type, axis=(1, 0, 0)):
    """Create Blender constraint representing a robot joint."""
    if not obj1 or not obj2:
        return None
    
    # Add appropriate constraint based on joint type
    if joint_type == 'revolute':
        constraint = obj2.constraints.new(type='LIMIT_ROTATION')
        constraint.use_limit_x = True
        constraint.use_limit_y = True  
        constraint.use_limit_z = True
    elif joint_type == 'prismatic':
        constraint = obj2.constraints.new(type='LIMIT_LOCATION')
        constraint.use_limit_x = True
        constraint.use_limit_y = True
        constraint.use_limit_z = True
    elif joint_type == 'fixed':
        constraint = obj2.constraints.new(type='CHILD_OF')
        constraint.target = obj1
    
    return constraint


def validate_robot_assembly(context):
    """Validate robot assembly for URDF export."""
    props = context.scene.comfyui_mcp
    
    errors = []
    warnings = []
    
    # Check robot name
    if not props.robot_name.strip():
        errors.append("Robot name is required")
    
    # Check selected objects
    selected = context.selected_objects
    if len(selected) < 1:
        errors.append("At least one object must be selected for export")
    
    # Check for mesh objects
    mesh_objects = [obj for obj in selected if obj.type == 'MESH']
    if not mesh_objects:
        warnings.append("No mesh objects selected - URDF will have no visual/collision geometry")
    
    # Check joints
    if not props.joints:
        warnings.append("No joints defined - robot will be static")
    
    # Check export path
    if not props.export_path.strip():
        errors.append("Export path is required")
    
    return errors, warnings