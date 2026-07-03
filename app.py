import streamlit as st
from parser import parse_query

st.title("Company Search")

query = st.text_input("what company are you looking for?")

if st.button("Search"):
    if query:
        filters = parse_query(query)
        st.write("Filters found:")
        st.json(filters)

