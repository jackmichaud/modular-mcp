import subprocess
import shlex
from typing import Optional
from server import mcp

# List of allowed commands for basic safety
# This can be modified based on needs and security requirements
ALLOWED_COMMANDS = {
    # File and directory operations
    'ls', 'dir', 'pwd', 'cat', 'head', 'tail', 'wc', 'tree',
    'stat', 'basename', 'dirname', 'find',

    # System information
    'date', 'uptime', 'whoami', 'hostname', 'uname', 'env',
    'arch', 'sw_vers', 'sysctl', 'id',

    # Network tools
    'ping', 'curl', 'wget', 'netstat', 'ip', 'dig', 'host',
    'nslookup', 'traceroute', 'ifconfig', 'whois',

    # Process information
    'ps', 'top', 'htop', 'uptime', 'vm_stat',

    # Text processing
    'grep', 'egrep', 'fgrep', 'sed', 'awk', 'sort', 'uniq',
    'cut', 'tr', 'diff', 'cmp', 'strings',

    # File system tools
    'df', 'du', 'mount', 'diskutil info', 'lsblk',

    # Package management (read-only)
    'apt list', 'dpkg -l', 'pip list', 'pip show', 'npm list', 'brew list',

    # Developer tools (read-only)
    'which', 'whereis', 'man', 'xcode-select -p',

    # Misc utilities
    'yes', 'cal', 'uptime', 'bc', 'echo', 'printf',
}

@mcp.tool()
def list_allowed_commands() -> str:
    """List all allowed commands."""
    return "\n".join(sorted(ALLOWED_COMMANDS))

def is_command_allowed(command: str) -> bool:
    """
    Check if the command is in the allowed list.
    
    Args:
        command: The command to check
        
    Returns:
        bool: True if command is allowed, False otherwise
    """
    base_cmd = shlex.split(command)[0]
    return base_cmd in ALLOWED_COMMANDS

@mcp.tool()
def execute_command(command: str, timeout: Optional[int] = 30) -> str:
    """Execute a shell command and return its output.
    
    Args:
        command: The shell command to execute
        timeout: Maximum execution time in seconds (default: 30)
        
    Returns:
        Command output or error message.
        
    Security Note:
        - Only pre-approved commands from ALLOWED_COMMANDS can be executed
        - Commands are split safely using shlex
        - Timeout prevents long-running commands
        - Shell=False prevents shell injection
    """
    try:
        # Security check
        if not is_command_allowed(command):
            return (f"Error: Command '{command}' not allowed. "
                   f"Allowed commands are: {', '.join(sorted(ALLOWED_COMMANDS))}")
        
        # Parse command safely
        args = shlex.split(command)
        
        # Execute command with safety parameters
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False  # Prevent shell injection
        )
        
        # Format output
        output = []
        if result.stdout:
            output.append("STDOUT:")
            output.append(result.stdout.strip())
        if result.stderr:
            output.append("STDERR:")
            output.append(result.stderr.strip())
        
        if result.returncode != 0:
            output.append(f"Exit code: {result.returncode}")
        
        return "\n".join(output) if output else "Command completed with no output."
        
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds"
    except subprocess.SubprocessError as e:
        return f"Error executing command: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"