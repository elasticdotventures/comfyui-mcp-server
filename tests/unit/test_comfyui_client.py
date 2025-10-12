"""Unit tests for ComfyUI client functionality."""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import json
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from client.comfyui import ComfyUI


class TestComfyUIClient:
    """Test ComfyUI client class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.comfy = ComfyUI("http://localhost:8188")
    
    def test_init(self):
        """Test ComfyUI client initialization."""
        assert self.comfy.url == "http://localhost:8188"
        assert self.comfy.authentication is None
        assert self.comfy.client_id is not None
        assert "Content-Type" in self.comfy.headers
    
    def test_init_with_auth(self):
        """Test ComfyUI client initialization with authentication."""
        comfy = ComfyUI("http://localhost:8188", authentication="Bearer token")
        assert comfy.authentication == "Bearer token"
        assert comfy.headers["Authorization"] == "Bearer token"
    
    @patch('urllib.request.urlopen')
    def test_get_image(self, mock_urlopen):
        """Test image retrieval."""
        mock_response = Mock()
        mock_response.read.return_value = b"fake_image_data"
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = self.comfy.get_image("test.png", "", "output")
        assert result == b"fake_image_data"
    
    @patch('urllib.request.urlopen')
    def test_get_history(self, mock_urlopen):
        """Test history retrieval."""
        test_history = {"prompt_123": {"outputs": {}}}
        mock_response = Mock()
        mock_response.read.return_value = json.dumps(test_history).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = self.comfy.get_history("prompt_123")
        assert result == test_history
    
    @patch('urllib.request.urlopen')
    def test_queue_prompt(self, mock_urlopen):
        """Test prompt queuing."""
        test_response = {"prompt_id": "test_123"}
        mock_response = Mock()
        mock_response.read.return_value = json.dumps(test_response).encode()
        mock_urlopen.return_value = mock_response
        
        prompt = {"test": "workflow"}
        result = self.comfy.queue_prompt(prompt)
        assert result == test_response
    
    def test_update_workflow_params_clip_text_encode(self):
        """Test workflow parameter updates for CLIPTextEncode."""
        workflow = {
            "1": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": "old prompt"}
            }
        }
        params = {"text": "new prompt"}
        
        self.comfy.update_workflow_params(workflow, params)
        assert workflow["1"]["inputs"]["text"] == "new prompt"
    
    def test_update_workflow_params_ksampler(self):
        """Test workflow parameter updates for KSampler."""
        workflow = {
            "1": {
                "class_type": "KSampler",
                "inputs": {"seed": 1, "steps": 10, "cfg": 7.0, "denoise": 0.8}
            }
        }
        params = {"seed": 42, "steps": 20, "cfg": 8.5, "denoise": 1.0}
        
        self.comfy.update_workflow_params(workflow, params)
        assert workflow["1"]["inputs"]["seed"] == 42
        assert workflow["1"]["inputs"]["steps"] == 20
        assert workflow["1"]["inputs"]["cfg"] == 8.5
        assert workflow["1"]["inputs"]["denoise"] == 1.0
    
    def test_update_workflow_params_no_params(self):
        """Test workflow parameter updates with no parameters."""
        workflow = {"1": {"class_type": "Test", "inputs": {"value": "original"}}}
        original = workflow.copy()
        
        self.comfy.update_workflow_params(workflow, None)
        assert workflow == original
        
        self.comfy.update_workflow_params(workflow, {})
        assert workflow == original


@pytest.mark.asyncio
class TestComfyUIAsync:
    """Test async ComfyUI functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.comfy = ComfyUI("http://localhost:8188")
    
    @patch.dict(os.environ, {"WORKFLOW_DIR": "test_workflows"})
    @patch('builtins.open')
    @patch('os.path.exists')
    @patch('websocket.WebSocket')
    async def test_process_workflow_from_file(self, mock_websocket, mock_exists, mock_open):
        """Test processing workflow from file."""
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = '{"test": "workflow"}'
        
        mock_ws = Mock()
        mock_websocket.return_value = mock_ws
        
        # Mock the get_images method
        with patch.object(self.comfy, 'get_images', return_value={"9": ["http://test.jpg"]}):
            result = await self.comfy.process_workflow("test_workflow", {}, return_url=True)
            assert "9" in result
    
    @patch('websocket.WebSocket')
    async def test_process_workflow_from_dict(self, mock_websocket):
        """Test processing workflow from dictionary."""
        workflow_dict = {"test": "workflow"}
        mock_ws = Mock()
        mock_websocket.return_value = mock_ws
        
        # Mock the get_images method
        with patch.object(self.comfy, 'get_images', return_value={"9": ["http://test.jpg"]}):
            result = await self.comfy.process_workflow(workflow_dict, {}, return_url=True)
            assert "9" in result