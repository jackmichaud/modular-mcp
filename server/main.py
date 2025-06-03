import importlib
import yaml
import contextlib
from server import mcp


def load_tools_from_config(config_path="server/config.yaml"):
    with open(config_path) as f:
        config = yaml.safe_load(f)
    for tool_path in config.get("tools", []):
        importlib.import_module(tool_path)


if __name__ == "__main__":
    load_tools_from_config()

    print("MCP server is running. Enter Ctrl+C to stop.")

    # Suppress traceback caused by KeyboardInterrupt inside anyio
    with contextlib.suppress(KeyboardInterrupt):
        mcp.run(transport='stdio')

    # Optional clean print (only works if sys.stdout not closed yet)
    try:
        print("\nMCP server shut down.")
    except ValueError:
        pass  # stdout was closed