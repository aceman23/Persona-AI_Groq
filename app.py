import os
from dotenv import load_dotenv
from groq import Groq
import pandas as pd
import streamlit as st
from streamlit_pills import pills
from share_state import get_server_state, set_server_state
from util import hide_header_footer

load_dotenv()

df_combined = pd.DataFrame()

# Read from personas_store.csv if it exists
if os.path.exists('personas_store.csv'):
    df_store = pd.read_csv('personas_store.csv')
    df_combined = pd.concat([df_combined, df_store], ignore_index=True)

# Read from persona.csv if it exists and combine
if os.path.exists('persona.csv'):
    df_gallery = pd.read_csv('persona.csv')
    df_combined = pd.concat([df_combined, df_gallery], ignore_index=True)

# Remove any duplicate personas based on the 'name' column
if not df_combined.empty:
    df_combined.drop_duplicates(subset=['name'], keep='first', inplace=True)

# Use df_combined for the rest of your code
df = df_combined

# ---- Load personas from CSV ----
def load_personas():
    if os.path.exists(PERSONA_FILE):
        return pd.read_csv(PERSONA_FILE).to_dict(orient="records")
    return []

# ---- Save personas to CSV ----
def save_personas(personas):
    df = pd.DataFrame(personas)
    df.to_csv(PERSONA_FILE, index=False)

# ---- Initialize session state ----
if "personas" not in st.session_state:
    st.session_state.personas = load_personas()
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}


# --- Page Config
st.set_page_config(page_title="Multi-IT Persona Gen-AI Demo", layout='wide', initial_sidebar_state='expanded')
hide_header_footer()


# ---- Persona Manager Sidebar ----
st.sidebar.header("🧑‍🎨 Persona Manager")

with st.sidebar.form("persona_form", clear_on_submit=True):
    if st.session_state.edit_index is not None:
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
        name = st.text_input("Persona Name")
        tone = st.selectbox("Tone", ["Friendly", "Professional", "Casual", "Formal", "Funny"])
        domain = st.text_input("Domain / Expertise")
        backstory = st.text_area("Backstory")
        submit_label = "➕ Add Persona"

    submitted = st.form_submit_button(submit_label)

    if submitted and name.strip():
        persona = {"name": name, "tone": tone, "domain": domain, "backstory": backstory}
        if st.session_state.edit_index is not None:
            st.session_state.personas[st.session_state.edit_index] = persona
            st.session_state.edit_index = None
            st.success(f"Persona '{name}' updated!")
        else:
            st.session_state.personas.append(persona)
            st.success(f"Persona '{name}' added!")
        save_personas(st.session_state.personas)


# ---- Persona Selector & Display in Sidebar ----
active_persona = None
if st.session_state.personas:
    persona_names = [p["name"] for p in st.session_state.personas]
    selected_name = st.sidebar.selectbox("Active Persona", persona_names)
    active_persona = next((p for p in st.session_state.personas if p["name"] == selected_name), None)

    # Edit/Delete buttons
    col1, col2 = st.sidebar.columns(2)
    if col1.button("✏️ Edit"):
        st.session_state.edit_index = persona_names.index(selected_name)
        st.experimental_rerun()
    if col2.button("🗑️ Delete"):
        st.session_state.personas = [p for p in st.session_state.personas if p["name"] != selected_name]
        save_personas(st.session_state.personas)
        st.session_state.chat_histories.pop(selected_name, None)
        st.success(f"Persona '{selected_name}' deleted!")
        st.experimental_rerun()

    st.sidebar.write("🎭 **Active Persona Details:**")
    st.sidebar.json(active_persona)

else:
    st.sidebar.info("No personas created yet. Add one above!")


# --- Main Page Content (Gallery) ---
st.header("Multi-IT Persona Gen-AI Demo", divider='rainbow')
st.caption(" Leveraging the power of Generative AI and Groq Cloud to create virtual IT personas...")

# The following code is now simplified as it uses st.session_state.personas directly
personas_list = st.session_state.personas
if personas_list:
    st.subheader("Explore All Personas")
    
# Create a dictionary to map each category to its icon
category_to_icon_map = {
    "All": "🎯",
    "IT Expert": "💻",
    "Help Desk": "👨‍💻",
    "SAP": "📈",
    "Data Scientist": "📊",
    "Network": "🌐",
    "Security": "🔒",
    "Hardware": "🔧",
    "Software": "🖥️",
    # Add more mappings as you add categories
}

# Get a list of unique categories from the DataFrame
unique_categories = ["All"] + df["Category"].unique().tolist()

# Create a list of icons that matches the order of the categories
icon_list = [category_to_icon_map.get(cat, "❓") for cat in unique_categories]

# Pass the dynamic lists to pills()
selected = pills("Category: ", unique_categories, icon_list)

    
    if selected_pill != "All":
        filtered_personas = [p for p in personas_list if p.get("category", "Uncategorized") == selected_pill]
    else:
        filtered_personas = personas_list

    # Create the grid
    num_cols = 4
    cols = st.columns(num_cols)
    for i, persona in enumerate(filtered_personas):
        with cols[i % num_cols]:
            with st.container(border=True):
                st.markdown(f"**Role**: {persona['name']}")
                st.markdown(f"**Tone**: {persona['tone']}")
                st.markdown(f"**Domain**: {persona['domain']}")
                if st.button('💬 Chat Now', key=f"chat_button_{persona['name']}"):
                    st.session_state.active_persona = persona
                    st.rerun()

else:
    st.info("No personas available to display. Please create one in the sidebar.")


# ---- Chat UI (Consolidated) ----
st.write("---")
if active_persona:
    st.subheader(f"💬 Chat with **{active_persona['name']}**")
    persona_name = active_persona["name"]

    if persona_name not in st.session_state.chat_histories:
        st.session_state.chat_histories[persona_name] = []

    # Display chat history
    for msg in st.session_state.chat_histories[persona_name]:
        role, content = msg["role"], msg["content"]
        if role == "user":
            st.chat_message("user").markdown(content)
        else:
            st.chat_message("assistant").markdown(content)

    # Chat input
    if prompt := st.chat_input("Type your message..."):
        user_message = {"role": "user", "content": prompt}
        st.session_state.chat_histories[persona_name].append(user_message)
        st.chat_message("user").markdown(prompt)

        system_prompt = f"""
        You are {active_persona['name']} with a {active_persona['tone']} tone.
        Your expertise is in {active_persona['domain']}.
        Backstory: {active_persona['backstory']}
        """

        try:
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            response = client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *st.session_state.chat_histories[persona_name],
                ]
            )
            ai_reply = response.choices[0].message.content
            st.session_state.chat_histories[persona_name].append({"role": "assistant", "content": ai_reply})
            st.chat_message("assistant").markdown(ai_reply)

        except Exception as e:
            st.error(f"An error occurred while calling the Groq API: {e}")
            st.session_state.chat_histories[persona_name].pop()
