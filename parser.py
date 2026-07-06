import json
import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

def load_business_models(path="companies.jsonl", cache_path="business_models_cache.json"):
    if os.path.exists(cache_path) and os.path.getmtime(cache_path) > os.path.getmtime(path):
        with open(cache_path, encoding="utf-8") as f:
            return json.load(f)

    models = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            company = json.loads(line)

            company_models = company.get("business_model")
            if company_models is None:
                company_models = []

            for model in company_models:
                if model not in models:
                    models.append(model)

    models.sort()

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(models, f)

    return models


BUSINESS_MODELS = load_business_models()

PROMPT_TEMPLATE = """
You are a query parser for a company qualification and ranking system.
Your job is to read a natural language query about companies and extract structured filters from it. You do not answer the query, you do not search for companies, you only extract the fields listed below.

Numeric operators dictionary:
- "more than X" and "over X" and "after X" = X+1
- "at least X" and "minimum X" = X
- "fewer than X" and "under X" and "before X" = X-1
- "up to X" = X

Extract the following fields:
- country: array of strings or null. A list of ISO 3166-1 alpha-2 country codes (e.g. "DE" for Germany, "RO" for Romania) for the countries the user wants companies from. If a single country is mentioned, return an array with just that one code. If a region or group of countries is mentioned (e.g. "Europe", "Scandinavia", "Nordics"), include the country codes of all countries that belong to that region. If no country or region is mentioned, use null.
- industry: string or null. The industry or sector the user is targeting (e.g. "fintech", "automotive manufacturing", "healthcare"). Use the term as close to the user's wording as possible, normalized to lowercase. If not mentioned, use null.
- min_employees: integer or null. The minimum number of employees required. Apply numeric operators above. If not mentioned, use null.
- max_employees: integer or null. The maximum number of employees allowed. Apply numeric operators above. If not mentioned, use null.
- exact_employees: integer or null. The exact number of employees required. If not mentioned, use null.
- min_revenue: number or null. The minimum annual revenue required, in USD, as a plain integer without commas or symbols (e.g. "50 million" → 50000000). Apply numeric operators above. If the user specifies a different currency, convert to approximate USD. If not mentioned, use null.
- max_revenue: number or null. The maximum annual revenue allowed, in USD, as a plain integer without commas or symbols. Apply numeric operators above. If the user specifies a different currency, convert to approximate USD. If not mentioned, use null.
- exact_revenue: number or null. The exact annual revenue required, in USD, as a plain integer without commas or symbols. If not mentioned, use null.
- is_public: boolean or null. true if the user explicitly wants publicly traded companies, false if the user explicitly wants private companies, null if not mentioned.
- business_model: array of strings or null. Use only values from this list: {business_models}. Include all that apply. If none are mentioned, use null.
- company_type: string or null. "manufacturer" if the user wants companies that manufacture/produce goods, "distributor" if the user wants companies that distribute/wholesale goods. If not mentioned, use null.
- min_year_founded: integer or null. The earliest founding year allowed. Apply numeric operators above. If not mentioned, use null.
- max_year_founded: integer or null. The latest founding year allowed. Apply numeric operators above. If not mentioned, use null.
- exact_year_founded: integer or null. The exact founding year required. If not mentioned, use null.

Rules:
- Return ONLY valid JSON, no explanations, no markdown formatting, no code blocks.
- Do not invent values that are not stated or clearly implied in the query.
- If a field is not mentioned, use null.
- Numbers must be plain integers, not strings.

Output format:
{
  "country": array of strings or null,
  "industry": string or null,
  "min_employees": number or null,
  "max_employees": number or null,
  "exact_employees": number or null,
  "min_revenue": number or null,
  "max_revenue": number or null,
  "exact_revenue": number or null,
  "is_public": boolean or null,
  "business_model": array of strings or null,
  "company_type": string or null,
  "min_year_founded": number or null,
  "max_year_founded": number or null,
  "exact_year_founded": number or null
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
