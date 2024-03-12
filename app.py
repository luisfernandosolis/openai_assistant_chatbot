import streamlit as st
import random
import time
from dotenv import load_dotenv
load_dotenv()
import os
from utils import run_excecuter
from openai import OpenAI



# Crear un threat
client=OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
assistant_id=os.getenv("ASSISTANT_ID")


st.title("Asistente de Ventas - Datapath")

# Initialize chat history
if "thread_id" not in st.session_state:
    st.session_state.thread_id = client.beta.threads.create().id
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def typewriter(text: str, speed: int):
    tokens = text.split()
    container = st.empty()
    for index in range(len(tokens) + 1):
        curr_full_text = " ".join(tokens[:index])
        container.markdown(curr_full_text)
        time.sleep(1 / speed)




# Accept user input
if prompt := st.chat_input("Escribir mensaje..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        ##texto generado por el asistente
        message_box=client.beta.threads.messages.create(thread_id=st.session_state.thread_id,role="user",content=prompt)
        ## ejecutar el run
        run=client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id
        )
        with st.spinner('Databot está escribiendo ...'):
            st.toast('Estamos agradecidos por tu contacto!', icon='🎉')
            run_excecuter(run)
            message_assistant=client.beta.threads.messages.list(thread_id=st.session_state.thread_id).data[0].content[0].text.value
        typewriter(message_assistant,50)



    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": message_assistant})