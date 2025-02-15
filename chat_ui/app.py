import streamlit as st
from openai_file import get_azure_openai_response_stream

def initialize_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

def display_chat_messages():
    """Display all messages in the chat interface."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def main():
    st.title("RAG Chat Interface")
    
    # Initialize session state
    initialize_session_state()
    
    # Display chat messages
    display_chat_messages()
    
    # Chat input
    if prompt := st.chat_input("What would you like to know?"):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Add assistant response to chat
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # Get streaming response from Azure OpenAI
                for response_chunk in get_azure_openai_response_stream(prompt, st.session_state.chat_history):
                    full_response += response_chunk
                    # Add a blinking cursor to show it's still thinking
                    message_placeholder.markdown(full_response + "▌")
                
                # Final update without the cursor
                message_placeholder.markdown(full_response)
                
                # Store assistant response
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                # Update chat history
                st.session_state.chat_history.append({"query": prompt, "response": full_response})
                
            except Exception as e:
                error_message = f"An error occurred: {str(e)}"
                message_placeholder.markdown(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})

if __name__ == "__main__":
    main()