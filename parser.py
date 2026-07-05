import json
import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

COMPANIES_FILE = "companies.jsonl"
BUSINESS_MODELS_CACHE_FILE = "business_models_cache.json"


def load_business_models(path=COMPANIES_FILE, cache_path=BUSINESS_MODELS_CACHE_FILE):
    if os.path.exists(cache_path) and os.path.getmtime(cache_path) > os.path.getmtime(path):
        with open(cache_path, encoding="utf-8") as f:
            return json.load(f)

    models = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            company = json.loads(line)
            for model in company.get("business_model") or []:
                models.add(model)
    models = sorted(models)

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(models, f)

    return models


BUSINESS_MODELS = load_business_models()

PROMPT_TEMPLATE = """
You are a query parser for a company qualification and ranking system.
Your job is to read a natural language query about companies and extract structured filters from it. You do not answer the query, you do not search for companies, you only extract the fields listed below.

Numeric operators dictionary:
- "more than X" and "over X" = X+1
- "at least X" and "minimum X" = X
- "fewer than X" and "under X" = X-1
- "up to X" = X

Extract the following fields:
- country: string or null. The ISO 3166-1 alpha-2 country code (e.g. "DE" for Germany, "RO" for Romania) for the country the user wants companies from. If multiple countries are mentioned, pick the most specific one stated. If no country is mentioned, use null.
- industry: string or null. The industry or sector the user is targeting (e.g. "fintech", "automotive manufacturing", "healthcare"). Use the term as close to the user's wording as possible, normalized to lowercase. If not mentioned, use null.
- min_employees: integer or null. The minimum number of employees required. Apply numeric operators above. If not mentioned, use null.
- max_employees: integer or null. The maximum number of employees allowed. Apply numeric operators above. If not mentioned, use null.
- exact_employees: integer or null. The exact number of employees required. If not mentioned, use null.
- min_revenue: number or null. The minimum annual revenue required, in USD, as a plain integer without commas or symbols (e.g. "50 million" → 50000000). Apply numeric operators above. If the user specifies a different currency, convert to approximate USD. If not mentioned, use null.
- max_revenue: number or null. The maximum annual revenue allowed, in USD, as a plain integer without commas or symbols. Apply numeric operators above. If the user specifies a different currency, convert to approximate USD. If not mentioned, use null.
- exact_revenue: number or null. The exact annual revenue required, in USD, as a plain integer without commas or symbols. If not mentioned, use null.
- is_public: boolean or null. true if the user explicitly wants publicly traded companies, false if the user explicitly wants private companies, null if not mentioned.
- business_model: array of strings or null. Use only values from this list: {business_models}. Include all that apply. If none are mentioned, use null.
- needs_reasoning: boolean. true if the query contains conditions that cannot be resolved by simple field matching alone. false if the query is a straightforward combination of the fields above. Never null.

Rules:
- Return ONLY valid JSON, no explanations, no markdown formatting, no code blocks.
- Do not invent values that are not stated or clearly implied in the query.
- If a field is not mentioned, use null (except needs_reasoning, which is always true or false).
- Numbers must be plain integers, not strings.

Output format:
{
  "country": string or null,
  "industry": string or null,
  "min_employees": number or null,
  "max_employees": number or null,
  "exact_employees": number or null,
  "min_revenue": number or null,
  "max_revenue": number or null,
  "exact_revenue": number or null,
  "is_public": boolean or null,
  "business_model": array of strings or null,
  "needs_reasoning": boolean
}

Query: {{user_query}}
"""


def parse_query(user_query):
    prompt = PROMPT_TEMPLATE.replace("{business_models}", ", ".join(BUSINESS_MODELS))
    prompt = prompt.replace("{{user_query}}", user_query)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text
    filters = json.loads(response_text)
    return filters
