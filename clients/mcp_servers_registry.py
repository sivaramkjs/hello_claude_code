from anthropic.types.beta import (
    BetaMCPToolConfigParam,
    BetaMCPToolsetParam,
    BetaRequestMCPServerURLDefinitionParam,
)

from config.anthropic_config import GITHUB_MCP_URL, GITHUB_TOKEN

MCPServer = BetaRequestMCPServerURLDefinitionParam
MCPToolset = BetaMCPToolsetParam
MCPToolConfig = BetaMCPToolConfigParam

_SERVER_DEFINITIONS: list[MCPServer] = [
    MCPServer(
        type="url",
        name="github",
        url=GITHUB_MCP_URL,
        authorization_token=GITHUB_TOKEN,
    ),
]

MCP_SERVERS: dict[str, MCPServer] = {
    server["name"]: server for server in _SERVER_DEFINITIONS
}
