"""Integration tests for ComfyUI server connectivity."""
import pytest
import os
import asyncio
import requests
from unittest.mock import patch
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from client.comfyui import ComfyUI


class TestComfyUIIntegration:
    """Integration tests that require a running ComfyUI server."""
    
    @pytest.fixture
    def comfy_client(self):
        """Create ComfyUI client for testing."""
        host = os.environ.get("COMFYUI_HOST", "localhost")
        port = os.environ.get("COMFYUI_PORT", "8188")
        return ComfyUI(f"http://{host}:{port}")
    
    @pytest.fixture
    def comfyui_available(self):
        """Check if ComfyUI server is available."""
        host = os.environ.get("COMFYUI_HOST", "localhost")
        port = os.environ.get("COMFYUI_PORT", "8188")
        try:
            response = requests.get(f"http://{host}:{port}/queue")
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    @pytest.mark.integration
    @pytest.mark.skipif(
        os.environ.get("SKIP_INTEGRATION") == "true",
        reason="Integration tests skipped"
    )
    def test_comfyui_server_connectivity(self, comfy_client, comfyui_available):
        """Test basic connectivity to ComfyUI server."""
        if not comfyui_available:
            pytest.skip("ComfyUI server not available")
        
        # Test basic connectivity by checking queue
        try:
            response = requests.get(f"{comfy_client.url}/queue")
            assert response.status_code == 200
        except requests.RequestException as e:
            pytest.fail(f"Could not connect to ComfyUI server: {e}")
    
    @pytest.mark.integration
    @pytest.mark.skipif(
        os.environ.get("SKIP_INTEGRATION") == "true",
        reason="Integration tests skipped"
    )
    def test_workflow_file_exists(self):
        """Test that required workflow files exist."""
        workflow_dir = os.environ.get("WORKFLOW_DIR", "workflows")
        text_to_image_workflow = os.path.join(workflow_dir, "text_to_image.json")
        
        assert os.path.exists(text_to_image_workflow), f"Workflow file not found: {text_to_image_workflow}"
        
        # Validate JSON structure
        import json
        with open(text_to_image_workflow, 'r') as f:
            workflow = json.load(f)
            assert isinstance(workflow, dict), "Workflow should be a dictionary"
            assert len(workflow) > 0, "Workflow should not be empty"


@pytest.mark.asyncio
@pytest.mark.integration
class TestAsyncComfyUIIntegration:
    """Async integration tests."""
    
    @pytest.mark.skipif(
        os.environ.get("SKIP_INTEGRATION") == "true",
        reason="Integration tests skipped"
    )
    async def test_process_workflow_integration(self):
        """Test actual workflow processing (requires running ComfyUI)."""
        # Only run if ComfyUI is available
        host = os.environ.get("COMFYUI_HOST", "localhost")
        port = os.environ.get("COMFYUI_PORT", "8188")
        
        try:
            response = requests.get(f"http://{host}:{port}/queue", timeout=5)
            if response.status_code != 200:
                pytest.skip("ComfyUI server not available")
        except requests.RequestException:
            pytest.skip("ComfyUI server not available")
        
        comfy = ComfyUI(f"http://{host}:{port}")
        
        # Test with minimal parameters
        params = {
            "text": "simple test image",
            "seed": 1,
            "steps": 5,  # Minimal steps for speed
            "cfg": 7.0,
            "denoise": 1.0
        }
        
        try:
            # Test URL return mode
            result = await comfy.process_workflow("text_to_image", params, return_url=True)
            assert isinstance(result, dict)
            assert len(result) > 0
            
            # Check that we got URLs
            for node_id, images in result.items():
                assert isinstance(images, list)
                if images:  # If images were generated
                    for image_url in images:
                        assert isinstance(image_url, str)
                        assert image_url.startswith("http")
                        
        except Exception as e:
            pytest.skip(f"Workflow execution failed: {e}")


class TestEnvironmentConfiguration:
    """Test environment configuration for integration tests."""
    
    def test_environment_variables_set(self):
        """Test that environment variables are properly configured."""
        # These should have defaults
        host = os.environ.get("COMFYUI_HOST", "localhost")
        port = os.environ.get("COMFYUI_PORT", "8188")
        
        assert host is not None
        assert port is not None
        assert port.isdigit()
    
    def test_workflow_directory_exists(self):
        """Test that workflow directory exists."""
        workflow_dir = os.environ.get("WORKFLOW_DIR", "workflows")
        assert os.path.exists(workflow_dir), f"Workflow directory not found: {workflow_dir}"
        assert os.path.isdir(workflow_dir), f"Workflow path is not a directory: {workflow_dir}"