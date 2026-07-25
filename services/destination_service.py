import json
import re
from pathlib import Path


def load_knowledge(country):
    path = Path("knowledge") / f"{country.lower()}.json"

    with open(path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    # 1. Remove Markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE)

    # 2. Extract ONLY the content between the first '{' and the last '}'
    #    This strips away dangling markdown links or text placed after the JSON ends.
    first_brace = text.find("{")
    last_brace = text.rfind("}")

    if first_brace != -1 and last_brace != -1:
        text = text[first_brace: last_brace + 1]

    # 3. Clean up stray markdown links inserted between properties (e.g., [title](url))
    text = re.sub(r'\]\s*\(https?://[^\)]+\)', "", text)
    text = re.sub(r'\[[^\]]+\]\s*\(https?://[^\)]+\)', "", text)

    # 4. Remove trailing commas before closing brackets/braces (common LLM flaw)
    text = re.sub(r",\s*([}\]])", r"\1", text)

    try:
        return json.loads(text)

    except json.JSONDecodeError as e:
        # Print the exact location of the error for debugging
        lines = text.splitlines()
        error_line = lines[e.lineno - 1] if e.lineno <= len(lines) else ""

        print("\n" + "=" * 80)
        print(f"Invalid JSON in: {path}")
        print(f"Error: {e.msg}")
        print(f"Line {e.lineno}, Column {e.colno}")
        print("-" * 80)
        print(error_line)
        print(" " * max(0, e.colno - 1) + "^")
        print("=" * 80)

        raise
