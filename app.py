import streamlit as st
from parser import parse_query
from embedding import search_companies

st.title("Company Search")

query = st.text_input("what company are you looking for?")

if st.button("Search"):
    if query:
        filters = parse_query(query)
        st.write("Filters found:")
        st.json(filters)

        results = search_companies(filters, query)

        table_rows = []
        for company in results:
            naics = company.get("primary_naics")
            if naics is None:
                industry = None
            else:
                industry = naics["label"]

            business_models = company.get("business_model")
            if business_models is None:
                business_models = []

            table_rows.append({
                "Name": company.get("operational_name"),
                "Website": company.get("website"),
                "Country": company["address"].get("country_code"),
                "Industry": industry,
                "Employees": company.get("employee_count"),
                "Revenue": company.get("revenue"),
                "Public": company.get("is_public"),
                "Business model": ", ".join(business_models),
            })

        st.dataframe(table_rows)

