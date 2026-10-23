import asyncio

from claude_platform_101.weather_tools import get_forecast, get_weather
from clients.anthropic_async_client import MODELS, Message, anthropic_async_client


async def tool_runner():
    runner = anthropic_async_client.beta.messages.tool_runner(
        model=MODELS["sonnet"],
        max_tokens=10240,
        thinking={"type": "adaptive", "display": "summarized"},
        output_config={"effort": "high"},
        tools=[get_weather, get_forecast],
        messages=[
            Message(
                role="user",
                content="Plan a 2-day roadtrip out of NewYork with one stop, "
                "weighing weather and drive time. Pick the best stop",
            )
        ],
    )

    response = await runner.until_done()
    for block in response.content:
        if block.type == "text":
            print(block.text)
    # async for message in runner:
    #     for block in message.content:
    #         print(f"{block.type}:")
    #         match block.type:
    #             case "text":
    #                 print(block.text)
    #             case "thinking":
    #                 print(block.thinking)


asyncio.run(tool_runner())
