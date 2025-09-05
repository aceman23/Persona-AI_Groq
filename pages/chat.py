import os
from dotenv import load_dotenv
from groq import Groq 
import uuid
import pandas as pd
from share_state import get_server_state, set_server_state
import streamlit as st
from dotenv import load_dotenv
from streamlit_pills import pills
from util import hide_header_footer



load_dotenv()

# ---- Persona Management ----
if "personas" not in st.session_state:
    st.session_state.personas = []

st.sidebar.header("🧑‍🎨 Persona Manager")

with st.sidebar.form("persona_form", clear_on_submit=True):
    name = st.text_input("Persona Name")
    tone = st.selectbox("Tone", ["Friendly", "Professional", "Casual", "Formal", "Funny"])
    domain = st.text_input("Domain / Expertise")
    backstory = st.text_area("Backstory")

    submitted = st.form_submit_button("➕ Add Persona")

    if submitted and name.strip():
        persona = {"name": name, "tone": tone, "domain": domain, "backstory": backstory}
        st.session_state.personas.append(persona)
        st.success(f"Persona '{name}' added!")

# ---- Persona Selection ----
active_persona = None
if st.session_state.personas:
    persona_names = [p["name"] for p in st.session_state.personas]
    selected = st.sidebar.selectbox("Active Persona", persona_names)
    active_persona = next((p for p in st.session_state.personas if p["name"] == selected), None)

if active_persona:
    st.write(f"💬 Chatting as **{active_persona['name']}**")
    st.write(f"Tone: {active_persona['tone']} | Domain: {active_persona['domain']}")
    st.write(f"Backstory: {active_persona['backstory']}")
else:
    st.info("👉 Please create or select a persona to start chatting.")

# ---- Groq Client ----
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

if active_persona:
    system_prompt = f"""
    You are {active_persona['name']} with a {active_persona['tone']} tone.
    Your expertise is in {active_persona['domain']}.
    Backstory: {active_persona['backstory']}
    """
else:
    system_prompt = "You are a helpful AI assistant."

# Example placeholder for how you'd use it:
# response = client.chat.completions.create(
#     model="llama3-8b-8192",
#     messages=[{"role": "system", "content": system_prompt},
#               {"role": "user", "content": user_input}]
# )
