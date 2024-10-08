import pandas as pd
import streamlit as st
from streamlit_pills import pills
from share_state import set_server_state
from util import hide_header_footer

st.set_page_config(page_title="Multi-IT Persona Gen-AI Demo",layout='wide', initial_sidebar_state='collapsed')

hide_header_footer()
st.markdown("""
            <style>
            div[data-testid="collapsedControl"]{
                    visibility: collapse;
            }
            section[data-testid="stSidebar"]{
                   visibility: collapse;
            }
            </style>
            """,unsafe_allow_html=True)



def open_chat(id,role,prompt,description):
    set_server_state("persona_id", id)
    set_server_state("persona_role", role)
    set_server_state("persona_prompt", prompt)
    set_server_state("description", description)

def persona_grid_cell(id,role,description,prompt):
    st.markdown(f"**ID: :** psn_id_{id}{role[:4]}")
    st.markdown(f"**Role**: {role}")
    st.markdown(f"**Description:** {description}")
    
    if st.button('💬 Chat Now',key=f"psn_id_{id}{role[:4]}",on_click=open_chat,args=(id,role,prompt,description)):
         st.switch_page('pages/chat.py')
         

st.header("Multi-IT Persona Gen-AI Demo", divider='rainbow')
st.caption(" Leveraging the power of Generative AI and Groq Cloud to create virtual IT personas. These AI-powered assistants can answer questions, troubleshoot issues, and provide support across various IT domains, enhancing efficiency and user satisfaction within your enterprise.")
st.caption(" Powered by: llama3-70b-8192 LLM Model")
st.caption(" Powered by: Groq Cloud 'LPU' Inference Engine")
st.caption(" Powered by: Streamlit")

df = pd.read_csv('persona.csv')
unique_categories_list  = df["Category"].unique().tolist()

categories_list = ["All",*unique_categories_list]
selected = pills("Category: ", categories_list,['💻','🐧','👨‍💻','💻','🔒','🔧','📡','💽','🤖'])

row1 = st.columns(4) 
row2 =  st.columns(4) 
row3 =  st.columns(4) 
row4 = st.columns(4) 
row5 = st.columns(4)

grid  = [ cell.container(border=True) for cell in row1+row2+row3+row4+row5]

if selected != "All":   
    df =  df[df['Category'] == format(selected)]

i = 0
for index,cell in df.iterrows():
    with grid[i]:
        persona_grid_cell(cell["Id"],cell["Role"],cell["Description"],cell["Prompt"])
    i = i + 1

