import streamlit as st
import pandas as pd

# ---- Session State for Personas ----
if "personas" not in st.session_state:
    st.session_state.personas = []

# ---- Persona Management UI ----
st.sidebar.header("🧑‍🎨 Persona Manager")

with st.sidebar.form("persona_form", clear_on_submit=True):
    name = st.text_input("Persona Name")
    tone = st.selectbox("Tone", ["Expert", "Professional", "Casual", "Formal", "Funny"])
    domain = st.text_input("Domain / Expertise", placeholder="e.g. Healthcare, Marketing, Finance")
    backstory = st.text_area("Backstory", placeholder="What’s this persona’s role, history, or style?")

    submitted = st.form_submit_button("➕ Add Persona")

    if submitted and name.strip():
        persona = {
            "name": name,
            "tone": tone,
            "domain": domain,
            "backstory": backstory,
        }
        st.session_state.personas.append(persona)
        st.success(f"Persona '{name}' added!")

# ---- Persona Selector ----
if st.session_state.personas:
    st.sidebar.subheader("Your Personas")
    persona_names = [p["name"] for p in st.session_state.personas]
    selected = st.sidebar.selectbox("Active Persona", persona_names)

    active_persona = next(p for p in st.session_state.personas if p["name"] == selected)

    st.sidebar.write("🎭 **Active Persona Details:**")
    st.sidebar.json(active_persona)

else:
    st.sidebar.info("No personas created yet. Add one above!")

# ---- Example: Use Active Persona in Chat ----
if st.session_state.personas:
    st.write(f"💬 Chatting as **{active_persona['name']}** "
             f"(Tone: {active_persona['tone']}, Domain: {active_persona['domain']})")
    st.write(f"Backstory: {active_persona['backstory']}")
