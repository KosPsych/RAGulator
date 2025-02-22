import streamlit as st
import re
import base64
import os
from io import BytesIO
import requests
import json
from PIL import Image
from openai_file import get_azure_openai_response_stream
from utils.prompts import generation_system_prompt, generation_user_prompt, title_system_prompt, title_user_prompt
from typing import List, Tuple
from streamlit_float import *
from router import Router
from datetime import datetime
from openai_acess import OpenAIModel
import uuid

openai_model = OpenAIModel()

def create_response_prompt(query, retr_results):
    documents = "".join(f"<document-{idx}>\nSource: page {i['pg_number']} of {i['pdf_name']}\n{i['document']}</document-{idx}>" for idx, i in enumerate(retr_results))
    return generation_system_prompt, generation_user_prompt.format(context=documents, question=query)

def retrieve_documents(query, top_k=5, chat_history=[]):
    url = os.getenv("RETRIEVE_URL")
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = {
        'query': query,
        'top_k': top_k,
        'chat_history': chat_history
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

def initialize_session_state():
    """Initialize session state variables."""
    if "conversations" not in st.session_state:
        st.session_state.conversations = {}
    if "initial" not in st.session_state:
        st.session_state.initial = True
    if "current_conversation_id" not in st.session_state:
        new_conversation_id = str(uuid.uuid4())
        st.session_state.current_conversation_id = new_conversation_id
        st.session_state.conversations[new_conversation_id] = {
            "messages": [],
            "chat_history": [],
            "image_list": [],
            "current_image_index": 0,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "title": "Empty Session"
        }
    if "messages" not in st.session_state:
        st.session_state.messages = st.session_state.conversations[st.session_state.current_conversation_id]["messages"]
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = st.session_state.conversations[st.session_state.current_conversation_id]["chat_history"]
    if "image_list" not in st.session_state:
        st.session_state.image_list = st.session_state.conversations[st.session_state.current_conversation_id]["image_list"]
    if "current_image_index" not in st.session_state:
        st.session_state.current_image_index = st.session_state.conversations[st.session_state.current_conversation_id]["current_image_index"]

def create_new_conversation():
    """Create a new conversation and set it as current."""
    new_conversation_id = str(uuid.uuid4())
    st.session_state.conversations[new_conversation_id] = {
        "messages": [],
        "chat_history": [],
        "image_list": [],
        "current_image_index": 0,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "initial": True,
        "title": "Empty Session"
    }
    switch_conversation(new_conversation_id)

def switch_conversation(conversation_id):
    """Switch to a different conversation."""
    st.session_state.current_conversation_id = conversation_id
    st.session_state.messages = st.session_state.conversations[conversation_id]["messages"]
    st.session_state.chat_history = st.session_state.conversations[conversation_id]["chat_history"]
    st.session_state.image_list = st.session_state.conversations[conversation_id]["image_list"]
    st.session_state.current_image_index = st.session_state.conversations[conversation_id]["current_image_index"]
    st.session_state.initial = st.session_state.conversations[conversation_id]["initial"]

def save_current_conversation_state():
    """Save the current conversation state."""
    conv_id = st.session_state.current_conversation_id
    st.session_state.conversations[conv_id]["messages"] = st.session_state.messages
    st.session_state.conversations[conv_id]["chat_history"] = st.session_state.chat_history
    st.session_state.conversations[conv_id]["image_list"] = st.session_state.image_list
    st.session_state.conversations[conv_id]["current_image_index"] = st.session_state.current_image_index
    st.session_state.conversations[conv_id]["initial"] = st.session_state.initial
    
    # Update conversation title based on first message if it exists
    if st.session_state.messages and st.session_state.conversations[conv_id]["title"] == "Empty Session":
        first_message = st.session_state.messages[0]["content"]
        # st.session_state.conversations[conv_id]["title"] = first_message[:30] + "..." if len(first_message) > 30 else first_message
        inputs = {
            'messages': [
            {"role": "system", "content": title_system_prompt},
            {"role": "user", "content": title_user_prompt.format(query=first_message)},
            ],
            'params': {
            'temperature': 0.5
            }
        }
        st.session_state.conversations[conv_id]["title"] = openai_model.predict(inputs)['response']
        # st.rerun()

def extract_image_references(retr_results: List):
    """Extract image references from a message."""
    return [("pg. " + i['pg_number']+ ' of ' + i['pdf_name'], i['img']) for i in retr_results]

# def display_chat_messages():
#     """Display all messages in the chat interface."""
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])

def display_chat_messages():
    """Display all messages in the chat interface."""
    for message in st.session_state.messages:
        if message["role"] == 'assistant':  
            with st.chat_message(message["role"], avatar='./athex_logo.png'):
                st.markdown(message["content"])
        else:
            with st.chat_message(message["role"], avatar='./user.jpg'):
                st.markdown(message["content"])

def main():
    st.set_page_config(page_title="CodeQuestAI", page_icon="🔍", layout="wide")

    st.components.v1.html(
    """
    <script>
    document.addEventListener('DOMContentLoaded', function () {
        // Function to insert the image
        function insertImage() {
            var sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');
            
            if (sidebar && !window.parent.document.getElementById('customSidebarImage')) {
                var img = document.createElement('img');
                img.src = 'https://www.athexgroup.gr/image/company_logo?img_id=41211&t=1740171290540';
                img.id = 'customSidebarImage';
                img.style.width = '50%';
                img.style.display = 'block';
                img.style.margin = '10px auto';

                // Insert the image at the top of the sidebar
                sidebar.insertBefore(img, sidebar.firstChild);
            }
        }

        // Ensure the image is inserted after page load
        window.onload = insertImage;
        setTimeout(insertImage, 1000);  // Fallback in case of delayed sidebar rendering
    });
    </script>        
    """, width=0, height=0
)

    float_init(theme=True, include_unstable_primary=False)
    
    initialize_session_state()

    col_history = st.sidebar
    
    with col_history:
        # New conversation button
        # if st.button("New Conversation", key="new_conv", use_container_width=True):
        #     create_new_conversation()
        #     st.rerun()

        st.title("Previous Conversations")
        
        st.divider()
        
        # Display conversation history
        for conv_id, conv_data in sorted(st.session_state.conversations.items(), 
                                       key=lambda x: x[1]["timestamp"], 
                                       reverse=True):
            # Create a clickable button for each conversation
            if st.button(
                f"{conv_data['title']}", 
                key=f"conv_{conv_id}",
                use_container_width=True,
                type="secondary" if conv_id != st.session_state.current_conversation_id else "primary"
            ):
                switch_conversation(conv_id)
                st.rerun()
    
    if st.session_state.initial:
        col_name, col_top_k, col_new_conv = st.columns([4, 1, 1], vertical_alignment="bottom")
        with col_name: st.title("ATHEX AI Nexus")
        # with col_top_k:
        #     top_k_selected = st.selectbox("Top_k (for debugging only)", list(range(1, 21)))
        with col_new_conv:
            if st.button("New Session", key="new_conv", use_container_width=True):
                create_new_conversation()
                st.session_state.initial = True
                st.rerun()

        chat_input_container = st.container(height=650)
        with chat_input_container:
            history = st.container(height=550, border=False)
            with history: display_chat_messages()
        
            prompt = st.chat_input("What would you like to know?") 
            if prompt:
                st.session_state.messages.append({"role": "user", "content": prompt})
                with history:
                    with st.chat_message("user", avatar='./user.jpg'):
                        st.markdown(prompt)
                
                with history:
                    # with st.chat_message("assistant"):
                    with st.chat_message("assistant", avatar='https://th.bing.com/th?id=ODLS.3cba8519-3202-4b12-afd2-d1d22eb58175&w=32&h=32&qlt=94&pcl=fffffa&o=6&pid=1.2'):
                        message_placeholder = st.empty()
                        full_response = ""
                        
                        try:
                            with st.spinner("Thinking..."):
                                do_retrieve, self_sym_prompt, self_user_prompt = Router(prompt, st.session_state.chat_history)
                            if do_retrieve:
                                with st.spinner(f"Retrieving information..."):
                                    st.session_state.image_list = []
                                    chat_history_api = [{"question": i['query'], "answer": i['response']} for i in st.session_state.chat_history]
                                    retrieval_results = retrieve_documents(prompt, top_k_selected, chat_history_api)
                                    s_prompt, u_prompt = create_response_prompt(prompt, retrieval_results)
                            else:
                                s_prompt, u_prompt = self_sym_prompt, self_user_prompt
                            for response_chunk in get_azure_openai_response_stream(s_prompt, u_prompt, st.session_state.chat_history):
                                full_response += response_chunk
                                message_placeholder.markdown(full_response + "▌")
                            
                            message_placeholder.markdown(full_response)
                            st.session_state.messages.append({"role": "assistant", "content": full_response})
                            st.session_state.chat_history.append({"query": prompt, "response": full_response})
                            
                            if do_retrieve:
                                references = extract_image_references(retrieval_results)
                                if len(references) > 0: st.session_state.initial = False
                                for ref, image_data in references:
                                    if not any(existing_ref == ref for existing_ref, _ in st.session_state.image_list):
                                        st.session_state.image_list.append((ref, image_data))
                            
                            # Save the current conversation state
                            save_current_conversation_state()
                            st.rerun()
                            
                        except Exception as e:
                            error_message = f"An error occurred: {str(e)}"
                            message_placeholder.markdown(error_message)
                            st.session_state.messages.append({"role": "assistant", "content": error_message})

################################# here is the og code ######################################################
    else:
        col_chat, col_images = st.columns([1.7, 1], vertical_alignment="bottom")
        
        top_k_selected = 7
        with col_chat:
            col_name, col_top_k, col_new_conv = st.columns([4, 1, 1], vertical_alignment="bottom")
            with col_name: st.title("ATHEX AI Nexus")
            # with col_top_k:
            #     top_k_selected = st.selectbox("Top_k (for debugging only)", list(range(1, 21)))
            with col_new_conv:
                if st.button("New Session", key="new_conv", use_container_width=True):
                    create_new_conversation()
                    st.session_state.initial = True
                    st.rerun()

            chat_input_container = st.container(height=650)
            with chat_input_container:
                history = st.container(height=550, border=False)
                with history: display_chat_messages()
            
                prompt = st.chat_input("What would you like to know?")    
                if prompt:
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with history:
                        with st.chat_message("user", avatar='./user.jpg'):
                            st.markdown(prompt)
                    
                    with history:
                        # with st.chat_message("assistant"):
                        with st.chat_message("assistant", avatar='https://th.bing.com/th?id=ODLS.3cba8519-3202-4b12-afd2-d1d22eb58175&w=32&h=32&qlt=94&pcl=fffffa&o=6&pid=1.2'):
                            message_placeholder = st.empty()
                            full_response = ""
                            
                            try:
                                with st.spinner("Thinking..."):
                                    do_retrieve, self_sym_prompt, self_user_prompt = Router(prompt, st.session_state.chat_history)
                                if do_retrieve:
                                    with st.spinner(f"Retrieving information..."):
                                        st.session_state.image_list = []
                                        chat_history_api = [{"question": i['query'], "answer": i['response']} for i in st.session_state.chat_history]
                                        retrieval_results = retrieve_documents(prompt, top_k_selected, chat_history_api)
                                        s_prompt, u_prompt = create_response_prompt(prompt, retrieval_results)
                                else:
                                    s_prompt, u_prompt = self_sym_prompt, self_user_prompt
                                for response_chunk in get_azure_openai_response_stream(s_prompt, u_prompt, st.session_state.chat_history):
                                    full_response += response_chunk
                                    message_placeholder.markdown(full_response + "▌")
                                
                                message_placeholder.markdown(full_response)
                                st.session_state.messages.append({"role": "assistant", "content": full_response})
                                st.session_state.chat_history.append({"query": prompt, "response": full_response})
                                
                                if do_retrieve:
                                    references = extract_image_references(retrieval_results)
                                    for ref, image_data in references:
                                        if not any(existing_ref == ref for existing_ref, _ in st.session_state.image_list):
                                            st.session_state.image_list.append((ref, image_data))
                                
                                # Save the current conversation state
                                save_current_conversation_state()
                                st.rerun()
                                
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
                    if st.button("Previous", key="left", use_container_width=True) and current_index > 0:
                        st.session_state.current_image_index -= 1
                        save_current_conversation_state()
                        st.rerun()
                with col2: st.markdown(f"<h8 style='text-align: center;'>{ref + f' ({current_index + 1}/{len(st.session_state.image_list)})'}</h8>", unsafe_allow_html=True)
                with col3:
                    if st.button("Next", key="right", use_container_width=True) and current_index < len(st.session_state.image_list) - 1:
                        st.session_state.current_image_index += 1
                        save_current_conversation_state()
                        st.rerun()
                with st.container(height=650, border=True):
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