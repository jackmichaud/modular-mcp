import subprocess
import sys

def execute_command(command):
    try:
        # Execute the command and capture output
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Get output and errors
        output, errors = process.communicate()
        
        # Return both output and errors
        return {
            'output': output,
            'errors': errors,
            'return_code': process.returncode
        }
    except Exception as e:
        return {
            'output': '',
            'errors': str(e),
            'return_code': 1
        }

def main():
    if len(sys.argv) < 2:
        print("Usage: python mcp.py <command>")
        sys.exit(1)
    
    # Combine all arguments into a single command
    command = ' '.join(sys.argv[1:])
    
    # Execute the command
    result = execute_command(command)
    
    # Print output and errors
    if result['output']:
        print("Output:")
        print(result['output'])
    if result['errors']:
        print("Errors:")
        print(result['errors'])
    
    sys.exit(result['return_code'])

if __name__ == "__main__":
    main()