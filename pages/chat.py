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

PERSONA_FILE = "personas_store.csv"

# ---- Load personas from CSV ----
def load_personas():
    if os.path.exists(PERSONA_FILE):
        return pd.read_csv(PERSONA_FILE).to_dict(orient="records")
    return []

# ---- Save personas to CSV ----
def save_personas(personas):
    df = pd.DataFrame(personas)
    df.to_csv(PERSONA_FILE, index=False)

# ---- Initialize personas in session ----
if "personas" not in st.session_state:
    st.session_state.personas = load_personas()

# ---- Persona Management ----
st.sidebar.header("🧑‍🎨 Persona Manager")

with st.sidebar.form("persona_form", clear_on_submit=True):
    name = st.text_input("Persona Name")
    tone = st.selectbox("Tone", ["Expert", "Professional", "Casual", "Formal", "Manager"])
    domain = st.text_input("Domain / Expertise")
    backstory = st.text_area("Backstory")

    submitted = st.form_submit_button("➕ Add Persona")

    if submitted and name.strip():
        persona = {"name": name, "tone": tone, "domain": domain, "backstory": backstory}
        st.session_state.personas.append(persona)
        save_personas(st.session_state.personas)  # persist to CSV
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
