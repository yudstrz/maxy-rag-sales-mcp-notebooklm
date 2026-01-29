import streamlit as st
import sys
from pathlib import Path

# --- Configuration ---
TARGET_NOTEBOOK_ID = "8d68d6e7-b095-47ab-b016-a69b7377ad9a"
PROJECT_ROOT = Path(__file__).parent
SRC_PATH = PROJECT_ROOT / "src"
COOKIES_PATH = PROJECT_ROOT / "cookies.txt"

# Add src to python path
sys.path.append(str(SRC_PATH))

# --- Page Setup ---
st.set_page_config(
    page_title="NotebookLM Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Clean CSS (Minimal) ---
# Hanya minimal styling untuk merapikan, tanpa merusak font icon
st.markdown("""
<style>
    /* Main container cleaner */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
        max-width: 800px;
    }
    
    /* Background halus (opsional, bisa dihapus jika ingin default putih) */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Chat bubbles styling */
    [data-testid="stChatMessage"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        color: #1e1e1e !important; /* Force dark text */
    }
    
    /* Ensure content inside bubbles is also dark */
    [data-testid="stChatMessage"] p, 
    [data-testid="stChatMessage"] div,
    [data-testid="stChatMessage"] span {
        color: #1e1e1e !important;
    }
    
    /* User message specific style */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background-color: #fff3e0; /* Light orange tint for user */
        border-color: #ffe0b2;
    }
    
    /* Hide header decorations */
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- Imports & Auth ---
try:
    from notebooklm_mcp.server import get_client
    from notebooklm_mcp.api_client import NotebookLMClient, extract_cookies_from_chrome_export
except ImportError:
    st.error("⚠️ Error: Could not import `notebooklm_mcp`. Please run from project root.")
    st.stop()

@st.cache_resource
def get_authenticated_client():
    """Load client securely with caching to prevent reload per interaction."""
    # 1. Try standard method (Environment/Cache)
    try:
        client = get_client()
        return client
    except Exception:
        pass
        
    # 2. Try cookies.txt fallback
    if COOKIES_PATH.exists():
        try:
            cookies = extract_cookies_from_chrome_export(COOKIES_PATH.read_text().strip())
            return NotebookLMClient(cookies=cookies)
        except Exception:
            pass
            
    return None

# --- Main App Logic ---

# Initialize Client
if "client" not in st.session_state:
    st.session_state.client = get_authenticated_client()

# Header
st.title("🤖 Chatbot Asisten")
st.caption("Diskusi langsung dengan referensi dari NotebookLM")

# Auth Check
if not st.session_state.client:
    st.warning("🔒 **Akses Ditolak**: Tidak dapat login ke NotebookLM.")
    st.info("💡 Solusi: Pastikan file `cookies.txt` ada d folder project dan valid.")
    st.stop()

# Session State for History
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Render Chat History ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Chat Input & Response ---
if prompt := st.chat_input("Ketik pesan Anda di sini..."):
    # 1. Show User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate Response
    with st.chat_message("assistant"):
        with st.spinner("Sedang mencari jawaban..."):
            try:
                response = st.session_state.client.query(
                    notebook_id=TARGET_NOTEBOOK_ID,
                    query_text=prompt
                )
                answer = response.get("answer", "Maaf, saya tidak menemukan jawaban.")
                
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
