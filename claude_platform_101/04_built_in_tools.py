import asyncio

from clients.anthropic_async_client import MODELS, Message, anthropic_async_client


# server tools - runs on Anthropic cloud sandbox, no agent loop required and no pushing back tool results
async def web_search():
    response = await anthropic_async_client.messages.create(
        model=MODELS["sonnet"],
        max_tokens=1024,
        tools=[{"type": "web_search_20260209", "name": "web_search"}],
        messages=[
            Message(
                role="user",
                content="What is the latest OpenAI latest model release? Answer in one sentence",
            )
        ],
    )

    for block in response.content:
        if block.type == "server_tool_use":
            print(f"Tool call: {block.name} — {block.input}")
        elif block.type == "text":
            print(block.text)


async def code_execution():
    response = await anthropic_async_client.messages.create(
        model=MODELS["sonnet"],
        max_tokens=1024,
        tools=[{"type": "code_execution_20260120", "name": "code_execution"}],
        messages=[
            Message(
                role="user",
                content="Calculate the mean and standard deviation of [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]. Show python code",
            )
        ],
    )

    for block in response.content:
        if block.type == "server_tool_use":
            print(f"Tool call: {block.name} — {block.input}")
        elif block.type == "bash_code_execution_tool_result":
            print(f"stdout: {block.content.stdout}")
        elif block.type == "text":
            print(f"text: {block.text}")


# asyncio.run(web_search())
asyncio.run(code_execution())
