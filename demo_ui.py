import streamlit as st
import sys
import re
from pathlib import Path

# --- Configuration ---
TARGET_NOTEBOOK_ID = "8d68d6e7-b095-47ab-b016-a69b7377ad9a"
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

# --- CSS ---
st.markdown("""
<style>
    /* Title and header - white for dark mode */
    h1, .stTitle, [data-testid="stHeading"] h1 {
        color: #ffffff !important;
    }
    
    /* Subtitle/caption */
    .stCaption, [data-testid="stCaption"], small {
        color: #cccccc !important;
    }
    
    /* Chat messages - white background, dark text */
    [data-testid="stChatMessage"] {
        background-color: #ffffff !important;
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] span,
    [data-testid="stChatMessage"] * {
        color: #1a1a1a !important;
    }
    
    /* Divider */
    hr {
        border-color: #444 !important;
    }
    
    /* Input area */
    textarea {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Header using Streamlit native ---
st.title("🤖 Maxy Chatbot")
st.caption("Asisten Virtual Maxy Academy")
st.divider()

# --- Import & Auth ---
try:
    from notebooklm_mcp.api_client import NotebookLMClient, extract_cookies_from_chrome_export
except ImportError:
    st.error("⚠️ Import error: notebooklm_mcp tidak ditemukan")
    st.stop()

@st.cache_resource
def get_client():
    """Load NotebookLM client from cache or cookies.txt"""
    # 1. Try loading from MCP cache (Managed by notebooklm-mcp-auth)
    try:
        from notebooklm_mcp.auth import load_cached_tokens
        tokens = load_cached_tokens()
        if tokens and tokens.cookies:
            # Check if tokens work
            client = NotebookLMClient(cookies=tokens.cookies)
            client.list_notebooks()
            return client, None
    except Exception:
        # If cache fails or is invalid, proceed to fallback
        pass

    # 2. Fallback to cookies.txt
    if not COOKIES_PATH.exists():
        return None, "File cookies.txt tidak ditemukan. Silakan jalankan `notebooklm-mcp-auth` di terminal."
    try:
        cookies = extract_cookies_from_chrome_export(COOKIES_PATH.read_text().strip())
        client = NotebookLMClient(cookies=cookies)
        client.list_notebooks()
        return client, None
    except Exception as e:
        return None, f"Auth Error: {e}. Coba jalankan `notebooklm-mcp-auth` untuk memperbaiki."

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
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Mencari jawaban..."):
            try:
                response = client.query(
                    notebook_id=TARGET_NOTEBOOK_ID,
                    query_text=prompt
                )
                answer = response.get("answer", "Maaf, tidak ada jawaban.")
                # Remove citations like [1], [2], [1, 2]
                answer = re.sub(r'\s*\[\d+(?:,\s*\d+)*\]', '', answer)
            except Exception as e:
                answer = f"Maaf, terjadi error: {e}"
        
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
