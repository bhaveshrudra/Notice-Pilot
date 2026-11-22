import os
import json
import re
from typing import Optional


def is_gemini_available() -> bool:
    """Check if GEMINI_API_KEY environment variable is configured."""
    return bool(os.environ.get('GEMINI_API_KEY'))


async def extract_with_gemini(text: str) -> Optional[dict]:
    """
    Extract structured notice data using Google Gemini API.
    Only executes if GEMINI_API_KEY is configured.
    Returns parsed dictionary conforming to ExtractedInfo or None on error/fallback.
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return None

    prompt = f"""You are an expert college notice parser. Extract structured information from the college notice below into a single JSON object.

Return ONLY a valid JSON object matching this schema:
{{
  "title": "string or null",
  "date": "YYYY-MM-DD or null (the main event date)",
  "time": "string or null",
  "location": "string or null",
  "registration_deadline": "YYYY-MM-DD or null",
  "requirements": ["list", "of", "strings"],
  "contact_info": ["list", "of", "strings"],
  "action_items": ["list", "of", "strings"],
  "evidence": [
    {{"field": "field_name", "snippet": "exact text snippet", "confidence": 0.95}}
  ],
  "uncertain_fields": ["list of fields that are ambiguous or low confidence"]
}}

CRITICAL RULES:
1. NEVER invent dates, locations, or requirements. Only extract what is present in the text.
2. Format all dates as YYYY-MM-DD.
3. If numeric dates (like 01/02/2026) are ambiguous between DD/MM and MM/DD, include "date" in uncertain_fields.
4. Return ONLY valid JSON, without any conversational preamble or postscript.

Notice text:
\"\"\"
{text}
\"\"\"
"""
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        if not response or not response.text:
            return None

        raw_text = response.text.strip()
        if "```" in raw_text:
            fence_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', raw_text)
            if fence_match:
                raw_text = fence_match.group(1).strip()

        data = json.loads(raw_text)
        if isinstance(data, dict):
            # Normalize schema fields
            data.setdefault("title", None)
            data.setdefault("date", None)
            data.setdefault("time", None)
            data.setdefault("location", None)
            data.setdefault("registration_deadline", None)
            data.setdefault("requirements", [])
            data.setdefault("contact_info", [])
            data.setdefault("action_items", [])
            data.setdefault("evidence", [])
            data.setdefault("uncertain_fields", [])
            return data

        return None
    except Exception:
        # Graceful fallback to local extraction
        return None
