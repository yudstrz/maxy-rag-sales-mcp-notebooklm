import streamlit as st
import os
import sys
from pathlib import Path
import time

# Add src to path to import notebooklm_mcp
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from notebooklm_mcp.server import get_client
    from notebooklm_mcp.api_client import NotebookLMClient
except ImportError:
    st.error("Could not import `notebooklm_mcp`. Please run this script from the project root.")
    st.stop()

st.set_page_config(page_title="NotebookLM Local Chat", page_icon="📓", layout="wide")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "curr_notebook_id" not in st.session_state:
    st.session_state.curr_notebook_id = None

def get_notebook_client():
    try:
        # Tries to load tokens from cache or env vars automatically
        return get_client()
    except Exception as e:
        return None

client = get_notebook_client()

with st.sidebar:
    st.title("📓 NotebookLM Chat")
    
    if not client:
        st.error("Authentication failed.")
        st.warning("Please run `notebooklm-mcp-auth` in your terminal first!")
        st.info("Or ensure Cookies are set in environment variables.")
        st.stop()
    
    st.success("Authenticated ✅")
    
    # Load notebooks
    with st.spinner("Loading notebooks..."):
        try:
            notebooks = client.list_notebooks()
            notebook_map = {nb.title: nb.id for nb in notebooks}
            
            selected_title = st.selectbox(
                "Select Notebook",
                options=list(notebook_map.keys()) if notebook_map else []
            )
            
            if selected_title:
                selected_id = notebook_map[selected_title]
                if selected_id != st.session_state.curr_notebook_id:
                    st.session_state.curr_notebook_id = selected_id
                    st.session_state.messages = [] # Reset chat on switch
                    st.toast(f"Switched to: {selected_title}")
                    
        except Exception as e:
            st.error(f"Failed to list notebooks: {str(e)}")

st.title("Chat with NotebookLM")

if not st.session_state.curr_notebook_id:
    st.info("👈 Please select a notebook from the sidebar to start chatting.")
else:
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask something about your notebook..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Determine conversation ID if we want threaded history
                    # For simple demo, we rely on the client's internal caching or stateless queries
                    # The MCP `notebook_query` tool uses conversation_id for context.
                    # Here we might need to manage it if we want multi-turn context.
                    # For now, let's treat each as a fresh query or let the client handle it if possible.
                    # The `notebook_query` tool signature: (notebook_id, query, source_ids=None, conversation_id=None)
                    
                    response = client.query(
                        notebook_id=st.session_state.curr_notebook_id,
                        query_text=prompt
                    )
                    
                    answer = response.get("answer", "No response.")
                    st.markdown(answer)
                    
                    # Save context if available (not implemented in this simple UI yet)
                    
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
