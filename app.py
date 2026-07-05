import streamlit as st
from parser import parse_query
from filters import filter_companies

st.title("Company Search")

query = st.text_input("what company are you looking for?")

if st.button("Search"):
    if query:
        filters = parse_query(query)
        st.write("Filters found:")
        st.json(filters)

        results = filter_companies(filters)
        st.write(f"Found {len(results)} companies:")
        st.json(results)

