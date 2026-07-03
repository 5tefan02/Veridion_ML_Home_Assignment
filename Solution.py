import streamlit as st

st.title("Company Search")

query = st.text_input("what company are you looking for?")

if st.button("Search"):
    if query:
        st.write("Results for:", query)

