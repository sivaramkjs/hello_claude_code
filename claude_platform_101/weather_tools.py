import json
import random

from anthropic import beta_async_tool


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
