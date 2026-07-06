import json
import anthropic
from dotenv import load_dotenv

from filters import load_companies, company_matches

load_dotenv()

client = anthropic.Anthropic()


def build_company_list_text(companies):
    lines = []
    for i in range(len(companies)):
        company = companies[i]

        name = company.get("operational_name")
        if name is None:
            name = "(no name)"

        description = company.get("description")
        if description is None:
            description = ""
        short_description = description[:200]

        line = str(i) + ". " + name + ": " + short_description
        lines.append(line)

    return "\n".join(lines)


def rank_by_relevance(companies, query_text):
    if len(companies) == 0:
        return []

    prompt = """
You are selecting and ranking companies that are relevant to a search query.

Query: """ + query_text + """

Companies:
""" + build_company_list_text(companies) + """

Only include company numbers that are actually relevant to the query. Do not include companies that clearly do not match what the query is asking for, even if they passed earlier filters. Return ONLY a JSON array of the relevant company numbers above, ordered from most relevant to least relevant. Include at most 20 numbers. Return ONLY valid JSON, no explanations, no markdown formatting, no code blocks.

Example output: [3, 0, 7, 1, 12]
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text
    order = json.loads(response_text)

    ranked_companies = []
    for index in order:
        ranked_companies.append(companies[index])

    return ranked_companies


def search_companies(filters, query_text, path="companies.jsonl"):
    companies = load_companies(path)

    filters["industry"] = None

    matched = []
    for company in companies:
        if company_matches(company, filters):
            matched.append(company)

    return rank_by_relevance(matched, query_text)
