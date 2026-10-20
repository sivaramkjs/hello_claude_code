import asyncio
import json
import random

from anthropic import beta_async_tool

from clients.anthropic_async_client import MODELS, Message, anthropic_async_client


@beta_async_tool
async def get_weather(location: str):
    return json.dumps(
        {"location": location, "temperature": "8C", "condition": "overcast"}
    )


@beta_async_tool
async def get_forecast(location: str):
    high_temps = ["15C", "16C", "17C", "18C", "19C", "20C"]
    low_temps = ["5C", "6C", "7C", "8C", "9C", "0C"]
    return json.dumps(
        [
            {
                "day": "Wed",
                "high": random.choice(high_temps),
                "low": random.choice(low_temps),
            },
            {
                "day": "Thu",
                "high": random.choice(high_temps),
                "low": random.choice(low_temps),
            },
            {
                "day": "Fri",
                "high": random.choice(high_temps),
                "low": random.choice(low_temps),
            },
        ]
    )


async def tool_runner():
    runner = anthropic_async_client.beta.messages.tool_runner(
        model=MODELS[0],
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
