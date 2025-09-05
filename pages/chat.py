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

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# ---- Persona Manager Sidebar ----
st.sidebar.header("🧑‍🎨 Persona Manager")

# Form for Add / Edit Persona
with st.sidebar.form("persona_form", clear_on_submit=True):
    if st.session_state.edit_index is not None:
        # Editing existing persona
        persona_to_edit = st.session_state.personas[st.session_state.edit_index]
        name = st.text_input("Persona Name", persona_to_edit["name"])
        tone = st.selectbox(
            "Tone",
            ["Friendly", "Professional", "Casual", "Formal", "Funny"],
            index=["Friendly", "Professional", "Casual", "Formal", "Funny"].index(persona_to_edit["tone"]),
        )
        domain = st.text_input("Domain / Expertise", persona_to_edit["domain"])
        backstory = st.text_area("Backstory", persona_to_edit["backstory"])
        submit_label = "💾 Update Persona"
    else:
        # Adding new persona
        name = st.text_input("Persona Name")
        tone = st.selectbox("Tone", ["Friendly", "Professional", "Casual", "Formal", "Funny"])
        domain = st.text_input("Domain / Expertise")
        backstory = st.text_area("Backstory")
        submit_label = "➕ Add Persona"

    submitted = st.form_submit_button(submit_label)

    if submitted and name.strip():
        persona = {"name": name, "tone": tone, "domain": domain, "backstory": backstory}

        if st.session_state.edit_index is not None:
            # Update existing persona
            st.session_state.personas[st.session_state.edit_index] = persona
            st.session_state.edit_index = None
            st.success(f"Persona '{name}' updated!")
        else:
            # Add new persona
            st.session_state.personas.append(persona)
            st.success(f"Persona '{name}' added!")

        save_personas(st.session_state.personas)

# ---- Persona Selection ----
active_persona = None
if st.session_state.personas:
    persona_names = [p["name"] for p in st.session_state.personas]
    selected = st.sidebar.selectbox("Active Persona", persona_names)
    active_persona = next((p for p in st.session_state.personas if p["name"] == selected), None)

    # Edit/Delete buttons
    col1, col2 = st.sidebar.columns(2)
    if col1.button("✏️ Edit"):
        st.session_state.edit_index = persona_names.index(selected)
        st.experimental_rerun()
    if col2.button("🗑️ Delete"):
        st.session_state.personas = [p for p in st.session_state.personas if p["name"] != selected]
        save_personas(st.session_state.personas)
        st.success(f"Persona '{selected}' deleted!")
        st.experimental_rerun()

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
