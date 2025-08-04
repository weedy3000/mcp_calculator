import asyncio
import json
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from arkitect.core.component.context.context import Context
from volcenginesdkarkruntime import AsyncArk
from dotenv import load_dotenv
import os
os.environ['ARK_API_KEY'] = "Your Doubao API Key"
load_dotenv()  # load environment variables from .env
client = AsyncArk(api_key=os.getenv('ARK_API_KEY'))
# function_calling调用方法
class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.client = client


    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
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

    async def process_query(self, query: str):
        """Process a query using Claude and available tools"""
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        response = await self.session.list_tools()
        available_tools = [tool for tool in response.tools]
        tool_functions = []
        for tool in available_tools:
            tool_dict = {
                  "type": "function",
                  "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                      "type": tool.inputSchema['type'],
                      "properties": tool.inputSchema['properties']
                      },
                      "required": tool.inputSchema['required']
                    }
                  }

            tool_functions.append(tool_dict)

        response = await self.client.chat.completions.create(
            model='doubao-1.5-pro-32k-250115',
            max_tokens=1000,
            messages=messages,
            tools=tool_functions
        )
        tool_call = response.choices[0].message.tool_calls[0]
        tool_result = await self.execute_tool(tool_call)
        print(f'工具{tool_call.function.name}调用结果：{tool_result}')
        return tool_result

    async def execute_tool(self,tool_call):
        toolname = tool_call.function.name
        params = json.loads(tool_call.function.arguments)
        result = await self.session.call_tool(toolname,params)
        print(result)
        tool_output = json.loads(result.content[0].text)['result']
        #print(tool_output)
        return tool_output

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery:").strip()

                if query.lower() == 'q':
                    break

                response = await self.process_query(query)
                print(response)

            except Exception as e:
                raise e


    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():
    client = MCPClient()
    try:
        await client.connect_to_server('mcp_tool.py')
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    import sys

    asyncio.run(main())