"""Unit tests for MCP server functionality."""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import json
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

# Mock the FastMCP import to avoid dependency issues in tests
with patch.dict('sys.modules', {'mcp.server.fastmcp': Mock()}):
    from server import text_to_image, download_image, run_workflow_from_file, run_workflow_from_json


class TestMCPServerTools:
    """Test MCP server tool functions."""
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"COMFYUI_HOST": "localhost", "COMFYUI_PORT": "8188"})
    @patch('server.ComfyUI')
    async def test_text_to_image(self, mock_comfyui_class):
        """Test text_to_image tool."""
        # Setup mock
        mock_comfyui = Mock()
        mock_comfyui.process_workflow = AsyncMock(return_value={"9": ["http://test.jpg"]})
        mock_comfyui_class.return_value = mock_comfyui
        
        # Test
        result = await text_to_image(
            prompt="test prompt",
            seed=42,
            steps=20,
            cfg=8.0,
            denoise=1.0
        )
        
        # Verify
        assert result == {"9": ["http://test.jpg"]}
        mock_comfyui.process_workflow.assert_called_once_with(
            "text_to_image",
            {"prompt": "test prompt", "seed": 42, "steps": 20, "cfg": 8.0, "denoise": 1.0},
            return_url=True
        )
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"RETURN_URL": "false"})
    @patch('server.ComfyUI')
    async def test_text_to_image_return_bytes(self, mock_comfyui_class):
        """Test text_to_image tool returning bytes."""
        # Setup mock
        mock_comfyui = Mock()
        mock_comfyui.process_workflow = AsyncMock(return_value={"9": [b"image_data"]})
        mock_comfyui_class.return_value = mock_comfyui
        
        # Test
        result = await text_to_image(
            prompt="test prompt",
            seed=42,
            steps=20,
            cfg=8.0,
            denoise=1.0
        )
        
        # Verify
        assert result == {"9": [b"image_data"]}
        mock_comfyui.process_workflow.assert_called_once_with(
            "text_to_image",
            {"prompt": "test prompt", "seed": 42, "steps": 20, "cfg": 8.0, "denoise": 1.0},
            return_url=False
        )
    
    @pytest.mark.asyncio
    @patch('urllib.request.urlretrieve')
    async def test_download_image(self, mock_urlretrieve):
        """Test download_image tool."""
        # Test
        result = await download_image("http://test.jpg", "/path/to/save.jpg")
        
        # Verify
        assert result == {"success": True}
        mock_urlretrieve.assert_called_once_with("http://test.jpg", "/path/to/save.jpg")
    
    @pytest.mark.asyncio
    @patch('builtins.open')
    @patch('server.ComfyUI')
    async def test_run_workflow_from_file(self, mock_comfyui_class, mock_open):
        """Test run_workflow_from_file tool."""
        # Setup mocks
        test_workflow = {"test": "workflow"}
        mock_open.return_value.__enter__.return_value = Mock()
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(test_workflow)
        
        mock_comfyui = Mock()
        mock_comfyui.process_workflow = AsyncMock(return_value={"9": ["http://test.jpg"]})
        mock_comfyui_class.return_value = mock_comfyui
        
        # Test
        result = await run_workflow_from_file("/path/to/workflow.json")
        
        # Verify
        assert result == {"9": ["http://test.jpg"]}
        mock_open.assert_called_once_with("/path/to/workflow.json", "r", encoding="utf-8")
        mock_comfyui.process_workflow.assert_called_once_with(
            test_workflow, {}, return_url=True
        )
    
    @pytest.mark.asyncio
    @patch('server.ComfyUI')
    async def test_run_workflow_from_json(self, mock_comfyui_class):
        """Test run_workflow_from_json tool."""
        # Setup mock
        test_workflow = {"test": "workflow"}
        mock_comfyui = Mock()
        mock_comfyui.process_workflow = AsyncMock(return_value={"9": ["http://test.jpg"]})
        mock_comfyui_class.return_value = mock_comfyui
        
        # Test
        result = await run_workflow_from_json(test_workflow)
        
        # Verify
        assert result == {"9": ["http://test.jpg"]}
        mock_comfyui.process_workflow.assert_called_once_with(
            test_workflow, {}, return_url=True
        )


class TestEnvironmentVariables:
    """Test environment variable handling."""
    
    @patch.dict(os.environ, {}, clear=True)
    def test_default_environment_values(self):
        """Test default environment variable values."""
        assert os.environ.get("COMFYUI_HOST", "localhost") == "localhost"
        assert os.environ.get("COMFYUI_PORT", "8188") == "8188"
        assert os.environ.get("RETURN_URL", "true") == "true"
        assert os.environ.get("MCP_TRANSPORT", "stdio") == "stdio"
    
    @patch.dict(os.environ, {
        "COMFYUI_HOST": "remote-host",
        "COMFYUI_PORT": "9999",
        "RETURN_URL": "false",
        "MCP_TRANSPORT": "sse"
    })
    def test_custom_environment_values(self):
        """Test custom environment variable values."""
        assert os.environ.get("COMFYUI_HOST") == "remote-host"
        assert os.environ.get("COMFYUI_PORT") == "9999"
        assert os.environ.get("RETURN_URL") == "false"
        assert os.environ.get("MCP_TRANSPORT") == "sse"