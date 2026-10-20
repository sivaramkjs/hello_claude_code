import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE_PATH = PROJECT_ROOT / ".env.local"

load_dotenv(ENV_FILE_PATH)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
