import asyncio

from clients.anthropic_async_client import MODELS, Message, anthropic_async_client
from clients.mcp_servers_registry import MCP_SERVERS, MCPToolConfig, MCPToolset


async def list_github_mcp_tools():
    github_mcp_server = MCP_SERVERS["github"]
    github_tool_configs: dict[str, MCPToolConfig] = {
        "search_repositories": {"enabled": True},
        "list_branches": {"enabled": True},
        "list_pull_requests": {"enabled": True},
        "create_branch": {"enabled": True},
        "search_code": {"enabled": True},
    }
    # filter which tools are allowed
    github_mcp_toolset = MCPToolset(
        type="mcp_toolset",
        mcp_server_name=github_mcp_server["name"],
        default_config={
            "enabled": False,
        },
        configs=github_tool_configs,
    )
    response = await anthropic_async_client.beta.messages.create(
        model=MODELS["sonnet"],
        max_tokens=1024,
        messages=[Message(role="user", content="List the exact tool names, one per line")],
        betas=["mcp-client-2025-11-20"],
        mcp_servers=[github_mcp_server],
        tools=[github_mcp_toolset],
    )
    # print(response)

for block in response.content:
        if block.type == "text":
            print(block.text)


asyncio.run(list_github_mcp_tools())