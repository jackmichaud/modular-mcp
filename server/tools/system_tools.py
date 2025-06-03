import os
from server import mcp

# Replaced with generalized shell tools

@mcp.tool()
def list_directory(path: str = ".") -> str:
    """List files and folders in a given directory.

    Args:
        path: Path to the directory (default is current directory)

    Returns:
        A newline-separated list of items or an error message.
    """
    try:
        items = os.listdir(path)
        return "\n".join(items) if items else "Directory is empty."
    except Exception as e:
        return f"Error listing directory: {e}"

@mcp.tool()
def read_file(filepath: str) -> str:
    """Read the contents of a file.

    Args:
        filepath: Path to the file

    Returns:
        File contents or error message.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

@mcp.tool()
def create_file(filepath: str, content: str = "") -> str:
    """Create a new file with optional content.

    Args:
        filepath: Path where the file will be created
        content: Content to write into the file

    Returns:
        Success message or error message.
    """
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File created at {filepath}"
    except Exception as e:
        return f"Error creating file: {e}"

@mcp.tool()
def delete_file(filepath: str) -> str:
    """Delete a file at the given path.

    Args:
        filepath: Path to the file to delete

    Returns:
        Success message or error message.
    """
    try:
        os.remove(filepath)
        return f"Deleted file: {filepath}"
    except Exception as e:
        return f"Error deleting file: {e}"
    