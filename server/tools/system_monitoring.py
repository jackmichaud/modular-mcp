from server import mcp
import psutil
import json

@mcp.tool()
def get_system_resources() -> str:
    """Get current system resource usage"""
    return json.dumps({
        "cpu_percent": psutil.cpu_percent(),
        "memory": dict(psutil.virtual_memory()._asdict()),
        "disk": dict(psutil.disk_usage('/')._asdict())
    })

@mcp.tool()
def get_process_info() -> str:
    """Get information about running processes"""
    process_list = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            process_list.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return json.dumps(process_list)