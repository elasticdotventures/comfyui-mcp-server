"""
MCP Client for Blender integration.
"""

import json
import socket
import asyncio
from typing import Dict, Any, Optional


class MCPClient:
    """Simple MCP client for communicating with ComfyUI MCP server."""
    
    def __init__(self, host: str = "localhost", port: int = 9000):
        self.host = host
        self.port = port
        self.socket = None
    
    def test_connection(self) -> bool:
        """Test if server is reachable."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def send_request(self, tool: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to MCP server via WebSocket."""
        try:
            import websocket
            
            ws_url = f"ws://{self.host}:{self.port}"
            ws = websocket.create_connection(ws_url, timeout=30)
            
            request = {
                "tool": tool,
                "params": json.dumps(params)
            }
            
            ws.send(json.dumps(request))
            response = ws.recv()
            ws.close()
            
            return json.loads(response)
            
        except Exception as e:
            return {"error": str(e)}
    
    def text_to_image(self, prompt: str, seed: int = 42, steps: int = 20, 
                     cfg: float = 8.0, denoise: float = 1.0) -> Dict[str, Any]:
        """Generate image using text_to_image tool."""
        params = {
            "prompt": prompt,
            "seed": seed,
            "steps": steps,
            "cfg": cfg,
            "denoise": denoise
        }
        return self.send_request("text_to_image", params)
    
    def download_image(self, url: str, save_path: str) -> Dict[str, Any]:
        """Download image using download_image tool."""
        params = {
            "url": url,
            "save_path": save_path
        }
        return self.send_request("download_image", params)
    
    def run_workflow_from_file(self, file_path: str) -> Dict[str, Any]:
        """Run workflow from file."""
        params = {
            "file_path": file_path
        }
        return self.send_request("run_workflow_from_file", params)
    
    def run_workflow_from_json(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run workflow from JSON data."""
        params = workflow_data
        return self.send_request("run_workflow_from_json", params)


# Async version for future use
class AsyncMCPClient:
    """Async MCP client for non-blocking operations."""
    
    def __init__(self, host: str = "localhost", port: int = 9000):
        self.host = host
        self.port = port
    
    async def send_request_async(self, tool: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send async request to MCP server."""
        try:
            import websockets
            
            ws_url = f"ws://{self.host}:{self.port}"
            
            async with websockets.connect(ws_url) as websocket:
                request = {
                    "tool": tool,
                    "params": json.dumps(params)
                }
                
                await websocket.send(json.dumps(request))
                response = await websocket.recv()
                
                return json.loads(response)
                
        except Exception as e:
            return {"error": str(e)}
    
    async def text_to_image_async(self, prompt: str, seed: int = 42, steps: int = 20,
                                 cfg: float = 8.0, denoise: float = 1.0) -> Dict[str, Any]:
        """Async image generation."""
        params = {
            "prompt": prompt,
            "seed": seed,
            "steps": steps,
            "cfg": cfg,
            "denoise": denoise
        }
        return await self.send_request_async("text_to_image", params)