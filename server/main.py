import importlib
import yaml

from server import mcp

def load_tools_from_config(config_path="config.yaml"):
    with open(config_path) as f:
        config = yaml.safe_load(f)
    for tool_path in config.get("tools", []):
        importlib.import_module(tool_path)

if __name__ == "__main__":
    load_tools_from_config()
    print("MCP server is running. Press Ctrl+C to stop.")
    mcp.run(transport='stdio')