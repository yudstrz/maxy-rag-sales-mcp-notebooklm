import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from notebooklm_mcp.server import get_client
    from notebooklm_mcp.api_client import NotebookLMClient, extract_cookies_from_chrome_export
except ImportError:
    st.error("Could not import `notebooklm_mcp`. Please run this script from the project root.")
    st.stop()

# --- Page Config ---
st.set_page_config(
    page_title="Chatbot Asisten",
    page_icon="🤖",
    layout="centered"
)

# --- Simple Custom Styling ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');
    
    * { font-family: 'Poppins', sans-serif !important; }
    
    .stApp {
        background: linear-gradient(135deg, #fff5f0 0%, #ffe0d1 100%);
    }
    
    [data-testid="stChatMessage"] {
        background: transparent !important;
    }
    
    /* User message avatar */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        flex-direction: row-reverse;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "client" not in st.session_state:
    st.session_state.client = None

# --- Authentication ---
def get_notebook_client():
    try:
        return get_client()
    except Exception:
        pass
    
    try:
        cookies_file = Path(__file__).parent / "cookies.txt"
        if cookies_file.exists():
            cookie_header = cookies_file.read_text().strip()
            if cookie_header:
                cookies = extract_cookies_from_chrome_export(cookie_header)
                return NotebookLMClient(cookies=cookies)
    except Exception:
        pass
    
    return None

if st.session_state.client is None:
    st.session_state.client = get_notebook_client()

# Hardcoded Notebook ID
TARGET_NOTEBOOK_ID = "8d68d6e7-b095-47ab-b016-a69b7377ad9a"

# --- Header ---
st.markdown("## 🤖 Chatbot Asisten")
st.caption("Powered by NotebookLM")

st.divider()

# --- Check Auth ---
if st.session_state.client is None:
    st.error("⚠️ Autentikasi gagal. Pastikan file `cookies.txt` berisi cookies yang valid.")
    st.stop()

# --- Display Chat History ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Welcome Message ---
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown("Halo! 👋 Selamat datang. Ada yang bisa saya bantu hari ini?")

# --- Chat Input ---
if prompt := st.chat_input("Ketik pesan..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Mengetik..."):
            try:
                response = st.session_state.client.query(
                    notebook_id=TARGET_NOTEBOOK_ID,
                    query_text=prompt
                )
                answer = response.get("answer", "Maaf, saya tidak bisa menjawab saat ini.")
            except Exception as e:
                answer = f"Terjadi kesalahan: {str(e)}"
        
        st.markdown(answer)
    
    # Save assistant message
    st.session_state.messages.append({"role": "assistant", "content": answer})
