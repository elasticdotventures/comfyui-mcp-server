# ComfyUI MCP Server - Blender Addon

A Blender addon that integrates with the ComfyUI MCP server for generative robotics and URDF export.

## Features

- **MCP Server Integration**: Connect to ComfyUI MCP server from within Blender
- **Generative Components**: Generate robot parts using natural language prompts
- **Robot Assembly**: Define kinematic joints and relationships
- **URDF Export**: Export complete robot assemblies to URDF format for simulation
- **Physics Validation**: Basic validation for physics simulation compatibility

## Installation

### Option 1: Install as Blender Addon

1. Zip the `comfyui_mcp` folder:
   ```bash
   cd blender_addon
   zip -r comfyui_mcp.zip comfyui_mcp/
   ```

2. In Blender:
   - Go to Edit → Preferences → Add-ons
   - Click "Install..." and select `comfyui_mcp.zip`
   - Enable "ComfyUI MCP Server" addon

### Option 2: Development Installation

1. Copy/symlink the addon to Blender's addons directory:
   ```bash
   # Linux/Mac
   ln -s $(pwd)/comfyui_mcp ~/.local/share/blender/4.0/scripts/addons/
   
   # Windows
   mklink /D "%APPDATA%\\Blender Foundation\\Blender\\4.0\\scripts\\addons\\comfyui_mcp" "path\\to\\comfyui_mcp"
   ```

2. Restart Blender and enable the addon

## Usage

### 1. Connect to MCP Server

1. Start your ComfyUI MCP server:
   ```bash
   uv run src/server.py
   ```

2. In Blender sidebar (N key), go to "ComfyUI MCP" tab
3. Set server host/port and click "Connect"

### 2. Generate Components

1. Select component type (joint, link, gripper, etc.)
2. Enter descriptive prompt (e.g., "robot arm joint with mounting holes")
3. Adjust generation parameters (seed, steps, CFG)
4. Click "Generate Component"

### 3. Define Robot Assembly

1. Add joints using "Add Joint" button
2. Configure joint properties:
   - Joint type (revolute, prismatic, fixed)
   - Axis of rotation/translation
   - Joint limits and dynamics
3. Select objects and create constraints with "Create Constraint"

### 4. Export to URDF

1. Select all objects to include in robot
2. Set robot name and export path
3. Choose mesh export format (STL, OBJ, DAE)
4. Click "Export URDF"

## File Structure

```
comfyui_mcp/
├── __init__.py          # Addon registration
├── operators.py         # Blender operators (generation, export)
├── panels.py           # UI panels in 3D viewport
├── utils.py            # Utility classes and functions
└── mcp_client/         # MCP client for server communication
    └── __init__.py
```

## Dependencies

### Required
- Blender 4.0+
- ComfyUI MCP Server (running)
- websocket-client (for MCP communication)

### Optional
- blend-my-bot (for advanced URDF features)
- urdfpy (for URDF validation)

## Workflow Integration

This addon integrates with:

1. **ComfyUI MCP Server** → Generate 3D components
2. **Blender Constraints** → Define kinematic relationships  
3. **URDF Export** → Physics simulation format
4. **External Tools**:
   - Gymnasium/MuJoCo for RL training
   - Gazebo for robotics simulation
   - PyBullet for physics validation

## Configuration

### Environment Variables

Set these in your ComfyUI MCP server `.env`:

```env
COMFYUI_HOST=localhost
COMFYUI_PORT=8188
RETURN_URL=true
MCP_TRANSPORT=stdio
```

### Blender Preferences

The addon stores connection settings in Blender's scene properties. Settings persist per blend file.

## Troubleshooting

### Connection Issues
- Ensure ComfyUI MCP server is running
- Check firewall settings for WebSocket port
- Verify host/port configuration

### Generation Issues  
- Check ComfyUI server logs for errors
- Ensure ComfyUI workflows exist in `workflows/` directory
- Verify ComfyUI models are loaded

### Export Issues
- Select objects before export
- Check export path permissions
- Ensure valid robot name (no special characters)

## Development

### Adding New Tools

1. Add MCP tool to `src/server.py`
2. Add operator to `operators.py`
3. Add UI to `panels.py`
4. Update MCP client methods

### Testing

```bash
# Run with Blender in background
blender --background --python test_addon.py

# Development with live reload
blender --python-expr "import bpy; bpy.ops.script.reload()"
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## License

Apache License 2.0 - See LICENSE file for details.