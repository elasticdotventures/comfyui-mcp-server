# ComfyUI MCP Server - Test and Workflow Management
# Idempotent commands for testing and workflow management

# Default recipe shows available commands
default:
    @just --list

# Test ComfyUI connectivity and SDXL workflow
test-sdxl:
    #!/usr/bin/env bash
    set -euo pipefail
    cd "{{justfile_directory()}}"
    source src/.env
    uv run --with websocket-client --with python-dotenv --with Pillow python test_sdxl.py

# Test all workflows
test-all: test-sdxl
    @echo "All tests completed"

# Validate workflow JSON files
validate-workflows:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Validating workflow files..."
    for workflow in workflows/*.json; do
        if jq empty "$workflow" 2>/dev/null; then
            echo "✓ $workflow is valid JSON"
        else
            echo "✗ $workflow is invalid JSON"
            exit 1
        fi
    done
    echo "All workflows validated successfully"

# Query available models from ComfyUI
query-models:
    #!/usr/bin/env bash
    set -euo pipefail
    source src/.env
    echo "Querying available models from $COMFYUI_HOST:$COMFYUI_PORT..."
    curl -s "http://$COMFYUI_HOST:$COMFYUI_PORT/object_info" | \
        jq -r '.CheckpointLoaderSimple.input.required.ckpt_name[0][]'

# Query ComfyUI system info
query-system:
    #!/usr/bin/env bash
    set -euo pipefail
    source src/.env
    echo "Querying system info from $COMFYUI_HOST:$COMFYUI_PORT..."
    curl -s "http://$COMFYUI_HOST:$COMFYUI_PORT/system_stats" | jq '.'

# Clean test output
clean:
    rm -rf test_output/
    @echo "Test output cleaned"

# Run MCP server in development mode
dev:
    uv run --with mcp --with websocket-client --with python-dotenv mcp dev src/server.py

# Run MCP server inspector
inspect:
    uv run --with mcp --with websocket-client --with python-dotenv mcp dev src/server.py --inspect
