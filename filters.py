import json
import ast

def load_companies(path="companies.jsonl"):
    companies = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            company = json.loads(line)

            address = company.get("address")
            if isinstance(address, str):
                address = ast.literal_eval(address)
            company["address"] = address

            primary_naics = company.get("primary_naics")
            if isinstance(primary_naics, str):
                primary_naics = ast.literal_eval(primary_naics)
            company["primary_naics"] = primary_naics

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
        country_code = company["address"].get("country_code")
        if country_code is None:
            country_code = ""
        country_code = country_code.lower()

        wanted_codes = []
        for code in filters["country"]:
            wanted_codes.append(code.lower())

        if country_code not in wanted_codes:
            return False

    if filters.get("industry"):
        naics = company.get("primary_naics")
        if naics is None:
            label = ""
        else:
            label = naics["label"]
        if filters["industry"].lower() not in label.lower():
            return False

    if not in_range(company.get("employee_count"), filters.get("min_employees"), filters.get("max_employees"), filters.get("exact_employees")):
        return False

    if not in_range(company.get("revenue"), filters.get("min_revenue"), filters.get("max_revenue"), filters.get("exact_revenue")):
        return False

    if not in_range(company.get("year_founded"), filters.get("min_year_founded"), filters.get("max_year_founded"), filters.get("exact_year_founded")):
        return False

    if filters.get("is_public") is not None:
        if company.get("is_public") != filters["is_public"]:
            return False

    if filters.get("business_model"):
        company_models = company.get("business_model")
        if company_models is None:
            company_models = []

        found_one = False
        for model in filters["business_model"]:
            if model in company_models:
                found_one = True

        if not found_one:
            return False

    if filters.get("company_type") == "manufacturer":
        naics = company.get("primary_naics")
        if naics is None:
            label = ""
        else:
            label = naics["label"]
        if "manufactur" not in label.lower():
            return False

    if filters.get("company_type") == "distributor":
        naics = company.get("primary_naics")
        if naics is None:
            label = ""
        else:
            label = naics["label"]
        if "wholesal" not in label.lower() and "distribut" not in label.lower():
            return False

    return True


def filter_companies(filters, path="companies.jsonl"):
    companies = load_companies(path)

    matched = []
    for company in companies:
        if company_matches(company, filters):
            matched.append(company)

    return matched
