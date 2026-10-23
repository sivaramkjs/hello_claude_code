import asyncio

from claude_platform_101.weather_tools import get_forecast, get_weather
from clients.anthropic_async_client import MODELS, anthropic_async_client

SYSTEM_PROMPT = """You are a seasoned trip guide"""
hist = [
    {
        "role": "user",
        "content": "I am building a recipe app. Help me name the main entities in the data model.",
    },
    {
        "role": "assistant",
        "content": "Start with Recipe, Ingredient, and Step. Add a RecipeIngredient entry that holds the quantity and unit for each ingredient in a recipe.",
    },
    {"role": "user", "content": "Good. Now suggest field names for Recipe."},
]


async def context_management_caching(message: str):
    """
    Prompt Caching
    """
    runner = anthropic_async_client.beta.messages.tool_runner(
        model=MODELS["sonnet"],
        max_tokens=10240,
        # Prompt caching works based on the incremental prefixes of cache break points or blocks.
        # Caches are model-specific, so the new model must create its own cache from scratch on the
        # next request—even if the tools, system prompt, and message history are byte-for-byte identical.
        # The input blocks cached in the order: tools, system, messages
        # Cache blocks with higher ttl must come before cache blocks with lower ttl. E.g., 1h -> 5m.
        # This is due to caching is prefix-based, so each cache entry is "everything from token 0 up to
        # this breakpoint." A later entry therefore contains the earlier one as part of itself.
        # E.g., 5m cache block expires before 1h cache block, which will make 1h cache block render useless.
        # Below top-level parameter enable automatic caching.
        cache_control={"type": "ephemeral", "ttl": "1h"},
        tools=[get_weather, get_forecast],  # Just-in-time context using tools
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                # "cache_control": {"type": "ephemeral"} # Explicit prompt caching
            }
        ],
        messages=[message],
    )

    # async for message_stream in runner:
    #     async for text in message_stream.text_stream:
    #         print(text, end="", flush=True)
    #
    #     message = await message_stream.get_final_message()

    response = await runner.until_done()
    usage = response.usage
    print(f"input tokens: {usage.input_tokens}")
    print(f"cache creation tokens: {usage.cache_creation_input_tokens}")
    print(f"cache read tokens: {usage.cache_read_input_tokens}")

    print(response)
    for block in response.content:
        if block.type == "text":
            print(block.text)


async def context_management_client_side_compaction(history: list):
    """
    Client Side Compaction
    """
    response = await anthropic_async_client.beta.messages.create(
        model=MODELS["opus"],
        max_tokens=1024,
        betas=["compact-2026-09-04"],
        # Client-side compaction: on-demand and more application control
        compaction={
            "type": "summarize",
            # optional explicit instructions instead of using API's own summarization prompt
            "instructions": "Summarize this recipe app design conversation. Preserve every entity and field name agreed so far, and the user's latest open request. Do not call tools; respond with the summary text only.",
        },
        messages=history,
    )

    print(response.model_dump_json(indent=2, exclude_none=True))
    for block in response.content:
        if block.type == "compaction":
            print(block.content)


# Filler to push the history past the 50,000 input token compaction trigger.
FILLER_NOTES = "The quick brown fox jumps over the lazy dog. " * 6000
messages = [
    {"role": "user", "content": f"Background notes, ignore for now:\n{FILLER_NOTES}"},
    {"role": "assistant", "content": "Noted."},
]


async def context_management_server_side_compaction(message: str):
    """
    Server Side Compaction
    """
    messages.append({"role": "user", "content": message})
    response = await anthropic_async_client.beta.messages.create(
        model=MODELS["opus"],
        max_tokens=1024,
        betas=["compact-2026-01-12"],
        # Server-side compaction: triggered when input tokens reach the threshold we set
        context_management={
            "edits": [
                {
                    "type": "compact_20260112",
                    # "pause_after_compaction": True,
                    "trigger": {"type": "input_tokens", "value": 50000},
                    # "instructions": "Focus on preserving code snippets, variable names, and technical decisions.",
                }
            ]
        },
        messages=messages,
    )

    # Append response (compaction blocks are automatically included)
    messages.append({"role": "assistant", "content": response.content})

    print(f"input tokens: {response.usage.input_tokens}")
    print(f"stop reason: {response.stop_reason}")
    print(response.model_dump_json(indent=2, exclude_none=True))
    # for block in response.content:
    #     if block.type == "text":
    #         print(block.text)


# asyncio.run(context_management_caching("Plan a 2-day roadtrip out of New York with one stop, "
#                                "weighing weather and drive time. Pick the best stop"))

# asyncio.run(context_management_client_side_compaction(hist))

asyncio.run(
    context_management_server_side_compaction("Help me build a Python web scraper")
)
