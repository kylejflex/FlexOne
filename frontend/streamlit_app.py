import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"

st.title("MCP Backend Client")

if st.button("Check Root (/)"):
    r = requests.get(f"{BACKEND_URL}/")
    st.json(r.json())

if st.button("Check Health (/health)"):
    r = requests.get(f"{BACKEND_URL}/health")
    st.write(r.text)
