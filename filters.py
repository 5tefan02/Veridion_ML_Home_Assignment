import json
import ast

COMPANIES_FILE = "companies.jsonl"


def parse_dict_field(value):
    if isinstance(value, str):
        return ast.literal_eval(value)
    return value


def load_companies(path=COMPANIES_FILE):
    companies = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            company = json.loads(line)
            company["address"] = parse_dict_field(company.get("address"))
            company["primary_naics"] = parse_dict_field(company.get("primary_naics"))
            companies.append(company)
    return companies


def in_range(value, min_value, max_value, exact_value):
    if min_value is not None and (value is None or value < min_value):
        return False
    if max_value is not None and (value is None or value > max_value):
        return False
    if exact_value is not None and value != exact_value:
        return False
    return True


def company_matches(company, filters):
    if filters.get("country"):
        country_code = company["address"].get("country_code") or ""
        if country_code.lower() != filters["country"].lower():
            return False

    if filters.get("industry"):
        naics = company.get("primary_naics")
        label = naics["label"] if naics else ""
        if filters["industry"].lower() not in label.lower():
            return False

    if not in_range(company.get("employee_count"), filters.get("min_employees"), filters.get("max_employees"), filters.get("exact_employees")):
        return False

    if not in_range(company.get("revenue"), filters.get("min_revenue"), filters.get("max_revenue"), filters.get("exact_revenue")):
        return False

    if filters.get("is_public") is not None:
        if company.get("is_public") != filters["is_public"]:
            return False

    if filters.get("business_model"):
        company_models = company.get("business_model") or []
        if not any(model in company_models for model in filters["business_model"]):
            return False

    return True


def filter_companies(filters, path=COMPANIES_FILE):
    companies = load_companies(path)
    return [company for company in companies if company_matches(company, filters)]
