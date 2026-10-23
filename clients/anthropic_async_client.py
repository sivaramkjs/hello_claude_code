from anthropic import AsyncAnthropic
from anthropic.types import MessageParam

from config.anthropic_config import ANTHROPIC_API_KEY

MODELS = {
    "sonnet": "claude-sonnet-5-5",
    "opus": "claude-opus-5-5",
    "haiku": "claude-haiku-5-5",
}


Message = MessageParam


anthropic_async_client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
