from pathlib import Path
from dotenv import load_dotenv
import os

_config_dir = Path(__file__).resolve().parents[1] / "config"
for env_file in [_config_dir / ".env", _config_dir / ".env.secret"]:
    load_dotenv(env_file)

import openai

key = os.environ.get("CEREBRAS_API_KEY")
if not key:
    print("CEREBRAS_API_KEY is not set")
    exit(1)

print(f"CEREBRAS_API_KEY loaded: {key[:8]}...")

client = openai.OpenAI(base_url="https://api.cerebras.ai/v1", api_key=key)
response = client.chat.completions.create(
    model="llama3.1-8b",
    messages=[{"role": "user", "content": "Say hello."}],
)
print("API call succeeded:", response.choices[0].message.content)
