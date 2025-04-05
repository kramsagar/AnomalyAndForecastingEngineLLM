# app.py
import streamlit as st
from agent_setup import agent

st.set_page_config(page_title="ML Anomaly Chatbot", layout="wide")
st.title("Anomaly Detection Chat Assistant")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

query = st.chat_input("Ask me to train or check anomaly...")

if query:
    st.session_state.chat_history.append(("user", query))
    with st.spinner("Thinking..."):
        response = agent.run(query)
    st.session_state.chat_history.append(("ai", response))

for role, message in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(message)
