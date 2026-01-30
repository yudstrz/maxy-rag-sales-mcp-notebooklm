import streamlit as st
import sys
from pathlib import Path

# --- Configuration ---
TARGET_NOTEBOOK_ID = "c317546a-d67c-4f6d-9460-bb02eaa6991f"
PROJECT_ROOT = Path(__file__).parent
SRC_PATH = PROJECT_ROOT / "src"
COOKIES_PATH = PROJECT_ROOT / "cookies.txt"

# Add src to python path
sys.path.insert(0, str(SRC_PATH))

# --- Page Setup ---
st.set_page_config(
    page_title="Maxy Chatbot",
    page_icon="🤖",
    layout="centered"
)

# --- Simple CSS ---
st.markdown("""
<style>
    .stApp {
        background-color: #f5f5f5;
    }
    .main-header {
        background: linear-gradient(135deg, #4169E1, #5a7df4);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        text-align: center;
    }
    .main-header h1 {
        color: white !important;
        margin: 0;
        font-size: 1.8rem;
    }
    .main-header p {
        color: rgba(255,255,255,0.9) !important;
        margin: 0.5rem 0 0 0;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="main-header">
    <h1>🤖 Maxy Chatbot</h1>
    <p>Asisten Virtual Maxy Academy</p>
</div>
""", unsafe_allow_html=True)

# --- Import & Auth ---
try:
    from notebooklm_mcp.api_client import NotebookLMClient, extract_cookies_from_chrome_export
except ImportError:
    st.error("⚠️ Import error: notebooklm_mcp tidak ditemukan")
    st.stop()

@st.cache_resource
def get_client():
    """Load NotebookLM client from cookies.txt"""
    if not COOKIES_PATH.exists():
        return None, "File cookies.txt tidak ditemukan"
    try:
        cookies = extract_cookies_from_chrome_export(COOKIES_PATH.read_text().strip())
        client = NotebookLMClient(cookies=cookies)
        # Test connection
        client.list_notebooks()
        return client, None
    except Exception as e:
        return None, str(e)

# Get client
client, error = get_client()

if not client:
    st.error(f"🔒 Gagal login ke NotebookLM: {error}")
    st.info("💡 Pastikan file `cookies.txt` berisi cookies yang valid dari NotebookLM")
    st.stop()

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Halo Kak! 👋 Selamat datang di Maxy Academy!\n\nAku MinMax, asisten virtual yang siap bantu Kakak. Ada yang bisa MinMax bantu?"}
    ]

# --- Display Chat ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Chat Input ---
if prompt := st.chat_input("Ketik pesan..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Mencari jawaban..."):
            try:
                response = client.query(
                    notebook_id=TARGET_NOTEBOOK_ID,
                    query_text=prompt
                )
                answer = response.get("answer", "Maaf, tidak ada jawaban.")
            except Exception as e:
                answer = f"Maaf, terjadi error: {e}"
        
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
