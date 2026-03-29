import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

TAXONOMY = """
CATEGORY 1 — EMOTIONAL MANIPULATION
  1.1 Fear Appeal: Exaggerates threat to provoke anxiety instead of informing
  1.2 Outrage Bait: Language designed to provoke anger rather than inform
  1.3 Appeal to Pity: Exploits sympathy to bypass rational evaluation

CATEGORY 2 — LOGICAL FALLACIES
  2.1 False Dichotomy: Presents only 2 options when more exist
  2.2 Slippery Slope: Claims one event inevitably leads to extreme outcome
  2.3 Hasty Generalization: Draws broad conclusion from insufficient evidence
  2.4 Strawman: Misrepresents opposing view in order to attack it

CATEGORY 3 — FRAMING MANIPULATION
  3.1 Cherry Picking: Selects only data that supports one narrative
  3.2 False Urgency: Manufactures time pressure to prevent critical thinking
  3.3 Loaded Language: Word choice that embeds assumption or bias
  3.4 Omission Bias: Leaves out context that would change the conclusion

CATEGORY 4 — AUTHORITY MANIPULATION
  4.1 Appeal to Authority: Uses credentials to shut down debate, not inform it
  4.2 Vague Attribution: "Experts say", "Sources claim" with no specifics
  4.3 Bandwagon: "Everyone believes" framing to pressure conformity
"""

def analyze_article(text: str) -> dict:
    prompt = f"""
You are an expert media literacy analyst. Analyze the following article text using the taxonomy below.

TAXONOMY:
{TAXONOMY}

ARTICLE:
{text}

Return ONLY a valid JSON object with exactly this structure, no extra text, no markdown fences:
{{
  "detected_patterns": [
    {{
      "category": "category name e.g. Emotional Manipulation",
      "subcategory": "subcategory name e.g. Fear Appeal",
      "quote": "exact short quote from the article that demonstrates this",
      "what_this_means": "plain English explanation of what this fallacy IS, for someone who has never heard of it. 2-3 sentences.",
      "why_its_problematic": "specifically why THIS instance in the article is misleading. 1-2 sentences.",
      "severity": <integer 1-10>
    }}
  ],
  "overall_manipulation_score": <float 1-10>,
  "political_leaning": {{
    "label": "Left / Centre-Left / Neutral / Centre-Right / Right",
    "confidence": <integer 0-100>,
    "key_signals": ["signal 1", "signal 2", "signal 3"]
  }},
  "factual_claims": [
    {{
      "claim": "a specific checkable factual claim from the article",
      "checkable": <true or false>,
      "verdict": "Likely True / Likely False / Unverifiable / Needs Expert Verification"
    }}
  ],
  "rhetorical_summary": "3-4 sentence plain English summary of the overall rhetorical strategy. What is it trying to make the reader feel or believe, and how?",
  "clean_rewrite": "Rewritten version of the article that conveys the same information but removes all manipulation, loaded language, and bias. Neutral and journalistic."
}}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=4000
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown fences if model adds them anyway
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    result = json.loads(raw)
    return result


# Quick test
if __name__ == "__main__":
    sample = """
    The economy is in CRISIS and experts warn we are heading toward
    total collapse. Everyone knows the current government has completely
    failed. Either we act now or we lose everything. Sources say millions
    will be affected. This is the worst situation in decades.
    """

    result = analyze_article(sample)
    print(json.dumps(result, indent=2))