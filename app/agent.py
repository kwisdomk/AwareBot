import os
import json
from pathlib import Path
from dotenv import load_dotenv
from google import genai

_client = None

def get_client():
    global _client
    if _client is None:
        # Explicitly load .env from project root
        ROOT_DIR = Path(__file__).parent.parent
        load_dotenv(ROOT_DIR / ".env")
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY missing in environment. Please ensure .env exists in the project root.")
        
        _client = genai.Client(api_key=api_key)
    return _client

# --- Path resolution ---
DATA_DIR = Path(__file__).parent / "data"
PROMPT_PATH = Path(__file__).parent / "prompts" / "system_prompt.txt"


def safe_parse(response: str) -> dict:
    """
    Safely extract JSON from model response.
    Handles markdown fences, extra text, and partial output.
    """
    text = response.strip()

    # Strip common markdown code fences
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Last resort: find the first { ... } block
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
        raise ValueError(f"Could not extract valid JSON from model response:\n{response}")


def run_agent(context: dict) -> dict:
    """
    Loads market signals + system prompt, sends structured context to Gemini,
    and returns a parsed JSON decision dict.
    """
    with open(DATA_DIR / "market_signals.json", "r") as f:
        signals = json.load(f)

    with open(DATA_DIR / "crop_prices.json", "r") as f:
        prices = json.load(f)

    prompt = PROMPT_PATH.read_text()

    full_input = f"""SYSTEM:
{prompt}

USER CONTEXT:
{json.dumps(context, indent=2)}

MARKET SIGNALS:
{json.dumps(signals, indent=2)}

CROP PRICE RANGES:
{json.dumps(prices, indent=2)}
"""

    client = get_client()
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=full_input
    )

    return safe_parse(response.text)
