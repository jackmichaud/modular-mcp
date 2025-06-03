import asyncio
from typing import Optional, List, Dict, Any
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv

import time

load_dotenv()  # load environment variables from .env

MAX_TOTAL_LOOPS = 10

class MCPClient:
    def __init__(self, window_size=20):
        """
        Initialize the MCP client with memory management.
        
        Args:
            window_size: Number of recent messages to keep in memory
        """
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
        
        # Persistent memory storage
        self.persistent_memory = []
        self.window_size = window_size
        
        # Recent conversation window
        self.messages: List[Dict[str, Any]] = [{
            "role": "system",
            "content": "You are a helpful assistant. You can use tools to answer questions and perform tasks. "
                       "Remember to use tools only when necessary, and always provide clear responses."
        }]
        
        # Context summary
        self.context_summary = ""

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server."""
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools, with memory management."""

        # Add user query
        self.messages.append({"role": "user", "content": query})
        
        # Add context summary if available
        if self.context_summary:
            self.messages.insert(1, {"role": "system", "content": f"Context summary: {self.context_summary}"})
        
        final_text = []


        tool_response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in tool_response.tools]

        loop_count = 0


        while loop_count < MAX_TOTAL_LOOPS:
            loop_count += 1

            # Send conversation so far to Claude
            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=self.messages,
                tools=available_tools
            )

            assistant_blocks = []
            tool_uses = []
            text_chunks = []

            # Separate content blocks
            for block in response.content:
                if block.type == "text":
                    assistant_blocks.append(block)
                    text_chunks.append(block.text)
                    print("AI: " + block.text)
                elif block.type == "tool_use":
                    tool_uses.append(block)
                    assistant_blocks.append(block)
                    text_chunks.append(f"[Tool call: {block.name}({block.input})]")

            # Add assistant message (whether just text, or tool calls)
            self.messages.append({"role": "assistant", "content": assistant_blocks})
            
            # Update persistent memory and context summary
            if len(text_chunks) > 1:  # Only summarize if there's substantial content
                # Add to persistent memory
                self.persistent_memory.append({
                    "timestamp": time.time(),
                    "content": "\n".join(text_chunks)
                })
                
                # Generate context summary if we have enough context
                if len(self.persistent_memory) > 5:  # Only summarize after 5 interactions
                    summary_response = self.anthropic.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=500,
                        messages=[
                            {"role": "system", "content": "Summarize the following conversation history in a concise way:"},
                            {"role": "user", "content": "\n".join(m["content"] for m in self.persistent_memory[-5:])}
                        ]
                    )
                    self.context_summary = summary_response.content[0].text
                
            # Maintain sliding window of recent messages
            if len(self.messages) > self.window_size:
                self.messages = self.messages[-self.window_size:]  # Keep only most recent messages
            final_text.append("\n".join(text_chunks))

            # If no tool use blocks, we're done
            if not tool_uses:
                break

            # Step 4: Call all requested tools and send tool_results back
            for tool_block in tool_uses:
                print(f"\n  [ Calling tool: {tool_block.name} with {len(tool_block.input)} inputs ]")
                result = await self.session.call_tool(tool_block.name, tool_block.input)
                self.messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": tool_block.id,
                        "content": result.content
                    }]
                })

            # Loop again: Claude will now respond to the tool_result(s)
        
        if loop_count == MAX_TOTAL_LOOPS:
            final_text.append("[⚠️ Reached max tool call depth — ending early.]")

        return "\n".join(final_text)
    
    async def call_tool(self, tool_name: str, input_data: Dict[str, Any]) -> str:
        """Call a specific tool with the given input."""
        if not self.session:
            raise RuntimeError("Not connected to any MCP server.")

        response = await self.session.call_tool(tool_name, input_data)
        return response.content if response else "No response from tool."

    async def chat_loop(self):
        """Run an interactive chat loop."""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\n\033[1mQuery: \033[0m").strip()
                if query.lower() == "quit":
                    break

                print()

                start_time = time.perf_counter()

                await self.process_query(query)

                elapsed = time.perf_counter() - start_time
                print(f"\n\033[1mResponse processed successfully in {elapsed:.2f} seconds\033[0m")


            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources."""
        await self.exit_stack.aclose()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())