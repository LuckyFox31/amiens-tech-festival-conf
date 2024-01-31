import os
import streamlit as st
import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import OpenAI
import time
from dotenv import load_dotenv

load_dotenv()

df = pd.DataFrame({
    "pays": [
        "United States", "United Kingdom", "France", "Germany", "Italy", "Spain", "Canada", "Australia", "Japan",
        "China"],
    "pib": [
        19294482071552, 2891615567872, 2411255037952, 3435817336832, 1745433788416, 1181205135360, 1607402389504,
        1490967855104, 4380756541440, 14631844184064
    ],
})


def append_message(message):
    if isinstance(message, SmartDataframe):
        st.dataframe(message)
    elif os.path.isfile(message):
        st.image(message)
    else:
        st.markdown(message)


def create_message(role, message):
    if not isinstance(message, SmartDataframe) and os.path.isfile(message):
        message = f'exports/charts/{time.time()}.png'
        os.rename('exports/charts/temp_chart.png', message)

    st.session_state.messages.append({
        'role': role,
        'content': message,
    })

    return message


st.title("Murmurer à l'oreille des données avec PandasAI et Streamlit")

if 'llm' not in st.session_state or 'df' not in st.session_state:
    st.session_state.llm = OpenAI(api_token=os.getenv("OPENAI_API_KEY"))
    st.session_state.df = SmartDataframe(df, config={'llm': st.session_state.llm})

if 'messages' not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        append_message(message['content'])

if prompt := st.chat_input("Posez votre question ici..."):
    user_message = create_message('user', prompt)

    with st.chat_message("user"):
        append_message(user_message)

    with st.spinner("Veuillez patienter..."):
        response = st.session_state.df.chat(prompt)
        assistant_message = create_message('assistant', response)
        with st.chat_message("assistant"):
            append_message(assistant_message)
