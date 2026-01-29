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

# --- CSS - Force Light Theme ---
st.markdown("""
<style>
    /* Force light background for entire app */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #f8f9fa !important;
    }
    
    /* Force ALL text to be dark */
    .stApp, .stApp * {
        color: #1a1a1a !important;
    }
    
    /* Main container */
    .block-container {
        padding-top: 0rem;
        padding-bottom: 5rem;
        max-width: 800px;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #4169E1 0%, #5a7df4 100%);
        padding: 1.5rem 2rem;
        border-radius: 0 0 16px 16px;
        margin-bottom: 1.5rem;
        margin-top: -1rem;
        margin-left: -2rem;
        margin-right: -2rem;
    }
    .header-title {
        color: white !important;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .header-subtitle {
        color: rgba(255, 255, 255, 0.85) !important;
        font-size: 0.95rem;
        margin-top: 0.3rem;
    }
    
    /* Chat bubbles */
    [data-testid="stChatMessage"] {
        background-color: #ffffff !important;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* User message style */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background-color: #fff3e0 !important;
        border-color: #ffe0b2;
    }
    
    /* Hide Streamlit branding */
    #MainMenu, header, footer {visibility: hidden; display: none;}
    
    /* Chat input styling */
    [data-testid="stChatInput"] textarea {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    
    /* Bottom container fix */
    [data-testid="stBottom"], [data-testid="stBottomBlockContainer"] {
        background-color: #f8f9fa !important;
    }
    
    /* Select box styling - make text blue */
    [data-testid="stSelectbox"] label,
    [data-testid="stSelectbox"] div[data-baseweb="select"] span {
        color: #4169E1 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Imports & Auth ---
try:
    from notebooklm_mcp.server import get_client
    from notebooklm_mcp.api_client import NotebookLMClient, extract_cookies_from_chrome_export
except ImportError:
    st.error("⚠️ Error: Could not import notebooklm_mcp.")
    st.stop()

@st.cache_resource
def get_authenticated_client():
    """Load client with caching."""
    try:
        return get_client()
    except Exception:
        pass
    
    if COOKIES_PATH.exists():
        try:
            cookies = extract_cookies_from_chrome_export(COOKIES_PATH.read_text().strip())
            return NotebookLMClient(cookies=cookies)
        except Exception:
            pass
    return None

# --- Initialize ---
if "client" not in st.session_state:
    st.session_state.client = get_authenticated_client()

if "messages" not in st.session_state:
    # Add welcome message from MinMax
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Halo Kak! Selamat datang di Maxy Academy! 👋\n\nAku MinMax, asisten virtual yang siap bantu Kakak cari info program bootcamp, magang, atau tips karir. Ada yang bisa MinMax bantu hari ini? 😊"
        }
    ]

# --- Header (using custom HTML with blue background) ---
st.markdown("""
<div class="header-container">
    <div class="header-title">🤖 Chatbot Asisten</div>
    <div class="header-subtitle">Diskusi langsung dengan referensi dari NotebookLM</div>
</div>
""", unsafe_allow_html=True)

# --- Auth Check ---
if not st.session_state.client:
    st.error("🔒 Akses Ditolak: Tidak dapat login ke NotebookLM.")
    st.info("💡 Pastikan file cookies.txt ada di folder project dan valid.")
    st.stop()

# --- Display Chat History ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Chat Input ---
if prompt := st.chat_input("Ketik pesan Anda..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
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
                st.error(f"Error: {e}")
