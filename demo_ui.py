import streamlit as st
import os
import sys
from pathlib import Path
from datetime import datetime

# Add src to path to import notebooklm_mcp
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from notebooklm_mcp.server import get_client
    from notebooklm_mcp.api_client import NotebookLMClient
except ImportError:
    st.error("Could not import `notebooklm_mcp`. Please run this script from the project root.")
    st.stop()

# --- Page Config ---
st.set_page_config(
    page_title="Chatbot Asisten",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS for Orange Gradient Theme ---
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap');

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Reset and Base */
    .stApp {
        font-family: 'Poppins', sans-serif !important;
        background: linear-gradient(135deg, #fff5f0 0%, #ffe0d1 100%) !important;
        min-height: 100vh;
    }
    
    /* Main container */
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* Chat Container */
    .chat-container {
        max-width: 450px;
        margin: 0 auto;
        background: #ffffff;
        border-radius: 25px;
        box-shadow: 0 15px 35px rgba(255, 126, 95, 0.2);
        overflow: hidden;
        display: flex;
        flex-direction: column;
        height: 90vh;
        margin-top: 2vh;
    }
    
    /* Header */
    .chat-header {
        background: linear-gradient(135deg, #ff7e5f, #feb47b);
        padding: 20px;
        display: flex;
        align-items: center;
        gap: 12px;
        color: white;
        box-shadow: 0 4px 15px rgba(255, 126, 95, 0.3);
    }
    
    .avatar {
        width: 50px;
        height: 50px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid rgba(255, 255, 255, 0.5);
        font-size: 24px;
    }
    
    .user-details h3 {
        font-size: 16px;
        font-weight: 600;
        margin: 0;
    }
    
    .user-details p {
        font-size: 12px;
        opacity: 0.9;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        background-color: #4cd137;
        border-radius: 50%;
        display: inline-block;
        border: 1px solid white;
    }
    
    /* Chat Body */
    .chat-body {
        flex: 1;
        padding: 20px;
        overflow-y: auto;
        background-color: #fffaf8;
        background-image: radial-gradient(#ff7e5f 0.5px, transparent 0.5px);
        background-size: 20px 20px;
    }
    
    /* Message Bubbles */
    .message {
        display: flex;
        flex-direction: column;
        margin-bottom: 15px;
        max-width: 85%;
        animation: fadeIn 0.3s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .message-content {
        padding: 12px 16px;
        font-size: 14px;
        line-height: 1.6;
        word-wrap: break-word;
    }
    
    .message-time {
        font-size: 10px;
        margin-top: 4px;
        color: #999;
    }
    
    /* Bot Message (Left) */
    .message.bot {
        align-self: flex-start;
    }
    
    .message.bot .message-content {
        background: white;
        color: #333;
        border-radius: 18px 18px 18px 2px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border: 1px solid #eee;
    }
    
    .message.bot .message-time {
        margin-left: 5px;
    }
    
    /* User Message (Right - Orange Gradient) */
    .message.user {
        align-self: flex-end;
        align-items: flex-end;
        margin-left: auto;
    }
    
    .message.user .message-content {
        background: linear-gradient(135deg, #ff7e5f, #feb47b);
        color: white;
        border-radius: 18px 18px 2px 18px;
        box-shadow: 0 4px 10px rgba(255, 126, 95, 0.3);
    }
    
    .message.user .message-time {
        margin-right: 5px;
    }
    
    /* Streamlit Chat Input Override */
    .stChatInput {
        background: white !important;
        border-top: 1px solid #eee !important;
        padding: 15px !important;
    }
    
    .stChatInput > div {
        background: #f5f5f5 !important;
        border-radius: 30px !important;
        border: 1px solid transparent !important;
    }
    
    .stChatInput > div:focus-within {
        background: white !important;
        border-color: #feb47b !important;
        box-shadow: 0 0 0 3px rgba(255, 126, 95, 0.1) !important;
    }
    
    .stChatInput textarea {
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* Streamlit Chat Message Override */
    .stChatMessage {
        background: transparent !important;
        padding: 0 !important;
    }
    
    [data-testid="stChatMessageContent"] {
        background: transparent !important;
    }
    
    /* Loading Spinner */
    .loading-dots {
        display: flex;
        gap: 4px;
        padding: 12px 16px;
    }
    
    .loading-dots span {
        width: 8px;
        height: 8px;
        background: #ff7e5f;
        border-radius: 50%;
        animation: bounce 1.4s infinite ease-in-out both;
    }
    
    .loading-dots span:nth-child(1) { animation-delay: -0.32s; }
    .loading-dots span:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
    }
    
    /* Responsive Mobile */
    @media (max-width: 480px) {
        .chat-container {
            width: 100%;
            height: 100vh;
            border-radius: 0;
            margin-top: 0;
        }
        
        .main .block-container {
            padding: 0 !important;
        }
    }
    
    /* Desktop adjustments */
    @media (min-width: 768px) {
        .chat-container {
            max-width: 420px;
            height: 85vh;
            margin-top: 5vh;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "curr_notebook_id" not in st.session_state:
    st.session_state.curr_notebook_id = None
if "client" not in st.session_state:
    st.session_state.client = None
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# --- Authentication ---
def get_notebook_client():
    """Try multiple authentication methods."""
    # Method 1: Try the standard get_client (uses cached tokens or env vars)
    try:
        return get_client()
    except Exception:
        pass
    
    # Method 2: Try loading from cookies.txt in project root
    try:
        from notebooklm_mcp.api_client import NotebookLMClient, extract_cookies_from_chrome_export
        
        cookies_file = Path(__file__).parent / "cookies.txt"
        if cookies_file.exists():
            cookie_header = cookies_file.read_text().strip()
            if cookie_header:
                cookies = extract_cookies_from_chrome_export(cookie_header)
                return NotebookLMClient(cookies=cookies)
    except Exception as e:
        pass
    
    return None

if st.session_state.client is None:
    st.session_state.client = get_notebook_client()
    if st.session_state.client:
        st.session_state.authenticated = True

# Hardcoded Notebook ID
TARGET_NOTEBOOK_ID = "8d68d6e7-b095-47ab-b016-a69b7377ad9a"
st.session_state.curr_notebook_id = TARGET_NOTEBOOK_ID

# --- Helper Functions ---
def get_current_time():
    return datetime.now().strftime("%H:%M")

def render_message(role, content, time_str):
    """Render a single message bubble."""
    role_class = "bot" if role == "assistant" else "user"
    return f"""
    <div class="message {role_class}">
        <div class="message-content">{content}</div>
        <div class="message-time">{time_str}</div>
    </div>
    """

# --- Main UI ---
# Header
st.markdown("""
<div class="chat-header">
    <div class="avatar">🤖</div>
    <div class="user-details">
        <h3>Chatbot Asisten</h3>
        <p><span class="status-dot"></span> Online</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Check Authentication
if not st.session_state.authenticated:
    st.markdown("""
    <div class="chat-body" style="display: flex; align-items: center; justify-content: center; flex-direction: column; gap: 10px;">
        <div style="background: white; padding: 20px; border-radius: 15px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <p style="color: #ff7e5f; font-weight: 600;">⚠️ Autentikasi Gagal</p>
            <p style="font-size: 12px; color: #666;">Jalankan <code>notebooklm-mcp-auth</code> di terminal terlebih dahulu.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Chat Body Container Start
st.markdown('<div class="chat-body" id="chatBody">', unsafe_allow_html=True)

# Display Welcome Message if no messages
if not st.session_state.messages:
    welcome_msg = "Halo! 👋 Selamat datang. Ada yang bisa saya bantu hari ini?"
    st.markdown(render_message("assistant", welcome_msg, get_current_time()), unsafe_allow_html=True)

# Display Chat History
for msg in st.session_state.messages:
    st.markdown(render_message(msg["role"], msg["content"], msg.get("time", "")), unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- Chat Input ---
if prompt := st.chat_input("Ketik pesan..."):
    current_time = get_current_time()
    
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "time": current_time
    })
    
    # Display user message immediately
    st.markdown(render_message("user", prompt, current_time), unsafe_allow_html=True)
    
    # Generate response
    with st.spinner(""):
        try:
            response = st.session_state.client.query(
                notebook_id=st.session_state.curr_notebook_id,
                query_text=prompt
            )
            answer = response.get("answer", "Maaf, saya tidak bisa menjawab saat ini.")
        except Exception as e:
            answer = f"Terjadi kesalahan: {str(e)}"
    
    response_time = get_current_time()
    
    # Add assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "time": response_time
    })
    
    # Rerun to display new messages
    st.rerun()
