import asyncio

from clients.anthropic_async_client import MODELS, Message, anthropic_async_client

tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city to get weather for",
                }
            },
            "required": ["city"],
        },
    },
    {
        "name": "find_restaurants",
        "description": "Find restaurants in a city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city to find restaurants for",
                }
            },
            "required": ["city"],
        },
    },
    {
        "name": "find_restaurants_by_city_and_cuisine",
        "description": "Find restaurants in a city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city to find restaurants for",
                },
                "cuisine": {
                    "type": "string",
                    "description": "The cuisine to find restaurants for",
                },
            },
            "required": ["city", "cuisine"],
        },
    },
]


async def run_tool(name, tool_input):
    if name == "get_weather":
        return f"Weather in {tool_input['city']}: 8C, sunny"
    if name == "find_restaurants":
        return f"Which restaurants do you want? {tool_input['city']}"
    if name == "find_restaurants_by_city_and_cuisine":
        return (
            f"There are Italian and Indian restaurants nearby in {tool_input['city']}"
        )
    raise ValueError(f"Unknown tool: {name}")


# messages = [Message(role="user", content="What should I wear in Berlin today?")]
messages = [Message(role="user", content="What should I eat in Berlin today?")]


async def agent_loop():
    turn = 0
    while True:
        turn += 1
        response = await anthropic_async_client.messages.create(
            model=MODELS["sonnet"], max_tokens=1024, tools=tools, messages=messages
        )

        print(f"--- turn: {turn} (stop_reason: {response.stop_reason}) ---")
        print(response.content)

        if response.stop_reason == "end_turn":
            for block in response.content:
                if block.type == "text":
                    print(block.text)
            break

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = await run_tool(block.name, block.input)
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        }
                    )
            messages.append(Message(role="assistant", content=response.content))
            messages.append(Message(role="user", content=tool_results))


asyncio.run(agent_loop())
