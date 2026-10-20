from dataclasses import dataclass

from anthropic import AsyncAnthropic
from anthropic.types import MessageParam

from config.anthropic_config import ANTHROPIC_API_KEY

MODELS = ['claude-sonnet-5-5', 'claude-opus-5-5', 'claude-haiku-5-5']


@dataclass
class Message(MessageParam):
    pass


anthropic_async_client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
