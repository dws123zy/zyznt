# _*_coding:utf-8 _*_

import traceback
import time
import logging
import threading
import importlib
import os
import httpx
from concurrent.futures import ThreadPoolExecutor  # 线程池
from fastapi import Request
import asyncio

from typing import Optional
from contextlib import AsyncExitStack
import json

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client

import os, re
from lxml import etree



# 本地模块



'''文件解析模块'''


'''日志'''

logger = logging.getLogger(__name__)




class MCPClient:
    def __init__(self):
        # 初始化会话和客户端对象
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        # 需要提前在.env文件中设置相关环境变量
        self.API_KEY = os.getenv("API_KEY")
        self.BASE_URL = os.getenv("BASE_URL")
        self.MODEL = os.getenv("MODEL")
        self.client = OpenAI(api_key=self.API_KEY, base_url=self.BASE_URL)
        self.sessions = {}
        self.messages = []
        with open("./MCP_Prompt.txt", "r", encoding="utf-8") as file:
            self.system_prompt = file.read()

    async def mcp_json_config(self, mcp_json_file):
        """
        从指定的JSON文件加载并解析MCP服务器配置，根据配置连接到活跃的MCP服务器。

        参数:
            mcp_json_file (str): MCP配置文件路径。

        抛出:
            ValueError: 如果配置无效或缺少必要字段。
        """
        try:
            with open(mcp_json_file, 'r') as f:
                mcp_config: dict = json.load(f)
        except json.JSONDecodeError:
            raise ValueError("Invalid MCP config")
        servers_config: dict = mcp_config.get('mcpServers', {})
        for k, v in servers_config.items():
            try:
                if v.get('isActive', False) == False:
                    continue
                print('-' * 50)
                mcp_name = v.get('name', k)
                mcp_type: str = v.get('type', 'stdio')
                if mcp_type.lower() == 'stdio':
                    command = v.get('command', None)
                    args = v.get('args', [])
                    env = v.get('env', {})
                    if command is None:
                        raise ValueError(f'{mcp_name} command is empty.')
                    if args == []:
                        raise ValueError(f'{mcp_name} args is empty.')
                    await self.connect_to_stdio_server(mcp_name, command, args, env)
                elif mcp_type.lower() == 'sse':
                    server_url = v.get('url', None)
                    if server_url is None:
                        raise ValueError(f'{mcp_name} server_url is empty.')
                    await self.connect_to_sse_server(mcp_name, server_url)
                elif mcp_type.lower() == 'streamable_http':
                    server_url = v.get('url', None)
                    if server_url is None:
                        raise ValueError(f'{mcp_name} server_url is empty.')
                    await self.connect_to_streamable_http_server(mcp_name, server_url)
                else:
                    raise ValueError(f'{mcp_name} mcp type must in [stdio, sse, streamable_http].')
            except Exception as e:
                print(f"Error connecting to {mcp_name}: {e}")

    async def connect_to_stdio_server(self, mcp_name, command: str, args: list[str], env: dict[str, str] = {}):
        """
        使用stdio协议连接到指定的MCP服务器。

        参数:
            mcp_name (str): MCP服务器名称。
            command (str): 启动服务器的命令。
            args (list[str]): 命令参数列表。
            env (dict[str, str]): 环境变量字典（可选）。
        """
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        self.sessions[mcp_name] = self.session

        await self.session.initialize()
        # 将MCP信息添加到system_prompt
        response = await self.session.list_tools()
        available_tools = [
            '##' + mcp_name + '\n### Available Tools\n- ' + tool.name + "\n" + tool.description + "\n" + json.dumps(
                tool.inputSchema) for tool in response.tools]
        self.system_prompt = self.system_prompt.replace("<$MCP_INFO$>", "\n".join(available_tools) + "\n<$MCP_INFO$>")
        tools = response.tools
        print(f"Successfully connected to {mcp_name} server with tools:", [tool.name for tool in tools])

    async def connect_to_sse_server(self, mcp_name, server_url: str):
        """
        使用SSE协议连接到指定的MCP服务器。

        参数:
            mcp_name (str): MCP服务器名称。
            server_url (str): 服务器的URL地址。
        """
        stdio_transport = await self.exit_stack.enter_async_context(sse_client(server_url))
        self.sse, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.sse, self.write))
        self.sessions[mcp_name] = self.session

        await self.session.initialize()
        # List available tools
        response = await self.session.list_tools()
        available_tools = [
            '##' + mcp_name + '\n### Available Tools\n- ' + tool.name + "\n" + tool.description + "\n" + json.dumps(
                tool.inputSchema) for tool in response.tools]
        self.system_prompt = self.system_prompt.replace("<$MCP_INFO$>", "\n".join(available_tools) + "\n<$MCP_INFO$>\n")
        tools = response.tools
        print(f"Successfully connected to {mcp_name} server with tools:", [tool.name for tool in tools])

    async def connect_to_streamable_http_server(self, mcp_name, server_url: str):
        """
        使用Streamable HTTP协议连接到指定的MCP服务器。

        参数:
            mcp_name (str): MCP服务器名称。
            server_url (str): 服务器的URL地址。
        """
        stdio_transport = await self.exit_stack.enter_async_context(streamablehttp_client(server_url))
        self.streamable_http, self.write, _ = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.streamable_http, self.write))
        self.sessions[mcp_name] = self.session

        await self.session.initialize()
        # List available tools
        response = await self.session.list_tools()
        available_tools = [
            '##' + mcp_name + '\n### Available Tools\n- ' + tool.name + "\n" + tool.description + "\n" + json.dumps(
                tool.inputSchema) for tool in response.tools]
        self.system_prompt = self.system_prompt.replace("<$MCP_INFO$>", "\n".join(available_tools) + "\n<$MCP_INFO$>\n")
        tools = response.tools
        print(f"Successfully connected to {mcp_name} server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """
        处理用户查询，使用OpenAI模型生成响应，并在需要时调用MCP工具。

        参数:
            query (str): 用户输入的查询字符串。

        返回:
            str: 最终处理结果的响应文本。
        """
        self.messages.append(
            {
                "role": "system",
                "content": self.system_prompt
            }
        )
        self.messages.append(
            {
                "role": "user",
                "content": query
            }
        )

        # Initial Claude API call
        response = self.client.chat.completions.create(
            model=self.MODEL,
            max_tokens=1024,
            messages=self.messages
        )

        # Process response and handle tool calls
        final_text = []
        content = response.choices[0].message.content
        if '<use_mcp_tool>' not in content:
            final_text.append(content)
        else:
            # 解析tool_string
            server_name, tool_name, tool_args = self.parse_tool_string(content)

            # 执行工具调用
            result = await self.sessions[server_name].call_tool(tool_name, tool_args)
            print(f"[Calling tool {tool_name} with args {tool_args}]")
            print("-" * 40)
            print("Server:", server_name)
            print("Tool:", tool_name)
            print("Args:", tool_args)
            print("-" * 40)
            print("Result:", result.content[0].text)
            print("-" * 40)
            self.messages.append({
                "role": "assistant",
                "content": content
            })
            self.messages.append({
                "role": "user",
                "content": f"[Tool {tool_name} \n returned: {result}]"
            })

            response = self.client.chat.completions.create(
                model=self.MODEL,
                max_tokens=1024,
                messages=self.messages
            )
            final_text.append(response.choices[0].message.content)
        return "\n".join(final_text)

    def parse_tool_string(self, tool_string: str) -> tuple[str, str, dict]:
        """
        解析包含MCP工具调用信息的字符串。

        参数:
            tool_string (str): 包含工具调用信息的字符串。

        返回:
            tuple[str, str, dict]: 包含服务器名、工具名和参数字典的元组。

        抛出:
            ValueError: 如果XML格式或JSON参数无效。
        """
        tool_string = re.findall("(<use_mcp_tool>.*?</use_mcp_tool>)", tool_string, re.S)[0]
        root = etree.fromstring(tool_string)
        server_name = root.find('server_name').text
        tool_name = root.find('tool_name').text
        try:
            tool_args = json.loads(root.find('arguments').text)
        except json.JSONDecodeError:
            raise ValueError("Invalid tool arguments")
        return server_name, tool_name, tool_args

    async def chat_loop(self):
        """
        运行一个交互式的聊天循环，持续接收用户输入并输出处理结果。
        """
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")
        self.messages = []
        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break
                if query.strip() == '':
                    print("Please enter a query.")
                    continue
                response = await self.process_query(query)
                print(response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """
        清理资源，关闭异步上下文管理器。
        """
        await self.exit_stack.aclose()


async def main():
    client = MCPClient()
    try:
        # await client.connect_to_sse_server('amap', 'https://mcp.amap.com/sse?key=d769f05385fe314e9b3ae548ba7d86b1')
        mcp_config_file = './mcp.json'
        await client.mcp_json_config(mcp_config_file)
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())


















