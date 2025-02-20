import streamlit as st
import re
import base64
import os
from io import BytesIO
import requests
import json
from PIL import Image
from openai_file import get_azure_openai_response_stream
from utils.prompts import generation_system_prompt, generation_user_prompt
from typing import List, Tuple
from streamlit_float import *

def create_response_prompt(query, retr_results):
    documents = "".join(f"<document-{idx}>\nSource: page {i['pg_number']} of {i['pdf_name']}\n{i['document']}</document-{idx}>" for idx, i in enumerate(retr_results))

    return generation_system_prompt, generation_user_prompt.format(context=documents, question=query)

# def retrieve_documents(query, top_k=5):
#     obj = GenerateResponseInput(query=query, top_k=top_k)
#     return generate_response(obj)

def retrieve_documents(query, top_k=5):
    url = os.getenv("OPENAI_API_URL")

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = {
        'query': query,
        'top_k': top_k
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()
    

# print(retrieve_documents(query="ensure that investors' rights are protected"))

def initialize_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "image_list" not in st.session_state:
        st.session_state.image_list = []
    if "current_image_index" not in st.session_state:
        st.session_state.current_image_index = 0

# def extract_image_references(message: str):
#     """Extract image references from a message."""
#     pattern = r'\[(.*?)\]'
#     references = re.findall(pattern, message)
#     return [(ref, get_sample_image_base64()) for ref in references]

def extract_image_references(retr_results: List):
    """Extract image references from a message."""

    return [("pg. " + i['pg_number']+ ' of ' + i['pdf_name'], i['img']) for i in retr_results]

def display_chat_messages():
    """Display all messages in the chat interface."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def main():
    st.set_page_config(page_title="CodeQuestAI", page_icon="🔍", layout="wide")
    float_init(theme=True, include_unstable_primary=False)
    
    initialize_session_state()
    
    col_chat, col_images = st.columns([1.7, 1], vertical_alignment="bottom")
    # col_chat, col_images = st.columns(2)
    
    with col_chat:
        st.title("RAG Chat Interface")
        
        chat_input_container = st.container(height=700)
        with chat_input_container:
            history = st.container(height=600, border=False)
            with history: display_chat_messages()
        
            prompt = st.chat_input("What would you like to know?")    
            if prompt:
                st.session_state.messages.append({"role": "user", "content": prompt})
                with history:
                    with st.chat_message("user"):
                        st.markdown(prompt)
                
                with history:
                    with st.chat_message("assistant"):
                        message_placeholder = st.empty()
                        full_response = ""
                        
                        try:
                            with st.spinner("Retrieving information..."):
                                st.session_state.image_list = []
                                retrieval_results = retrieve_documents(prompt, 3)
                                s_prompt, u_prompt = create_response_prompt(prompt, retrieval_results)
                            for response_chunk in get_azure_openai_response_stream(s_prompt, u_prompt, st.session_state.chat_history):
                                full_response += response_chunk
                                message_placeholder.markdown(full_response + "▌")
                            
                            message_placeholder.markdown(full_response)
                            st.session_state.messages.append({"role": "assistant", "content": full_response})
                            st.session_state.chat_history.append({"query": prompt, "response": full_response})
                            
                            references = extract_image_references(retrieval_results)
                            for ref, image_data in references:
                                if not any(existing_ref == ref for existing_ref, _ in st.session_state.image_list):
                                    st.session_state.image_list.append((ref, image_data))

                            # with history: display_chat_messages()
                            
                        except Exception as e:
                            error_message = f"An error occurred: {str(e)}"
                            message_placeholder.markdown(error_message)
                            st.session_state.messages.append({"role": "assistant", "content": error_message})
    
    with col_images:
        if st.session_state.image_list:
            current_index = st.session_state.current_image_index
            ref, image_data = st.session_state.image_list[current_index]
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                # if st.button("⬅️", key="left", type='tertiary', use_container_width=True) and current_index > 0:
                if st.button("Previous", key="left", use_container_width=True) and current_index > 0:
                    st.session_state.current_image_index -= 1
                    st.rerun()
            with col2: st.markdown(f"<h5 style='text-align: center;'>{ref + f' ({current_index + 1}/{len(st.session_state.image_list)})'}</h5>", unsafe_allow_html=True)
            with col3:
                if st.button("Next", key="right", use_container_width=True) and current_index < len(st.session_state.image_list) - 1:
                    st.session_state.current_image_index += 1
                    st.rerun()
            with st.container(height=700, border=True):
                st.image(f"data:image/png;base64,{image_data}", width=700)
    st.html(
    """
<style>
    .stAppHeader {
    display: none;
}
</style>
"""
)

if __name__ == "__main__":
    main()