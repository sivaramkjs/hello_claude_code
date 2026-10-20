import asyncio

from clients.anthropic_async_client import MODELS, Message, anthropic_async_client

SYSTEMS = {
    'reviewer' : 'You are a senior engineer. Give feedback in one paragraph. Be concise.',
    'tutor' : 'You are a tutor. Explain in simplest way possible. Be concise.',
}

async def process_message(messages: list[Message]):
    for model in MODELS:
        response = await anthropic_async_client.messages.create(
            model=model,
            max_tokens=1024,
            system=SYSTEMS['reviewer'],
            messages=messages
        )
        print(model, response.usage)
        for block in response.content:
            if block.type == "text":
                print(block.text)

MESSAGES = [
Message(role="user", content=f"Review this code: def add(a, b): \n return a - b",),
Message(role="user", content=f"What is prompt caching?",),
]
asyncio.run(process_message([MESSAGES[0]]))
