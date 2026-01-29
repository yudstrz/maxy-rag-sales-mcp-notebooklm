import streamlit as st
import os
import sys
from pathlib import Path
from datetime import datetime

# Add src to path to import notebooklm_mcp
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
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS ---
st.markdown("""
<style>
    /* Import Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap');
    
    /* Hide Streamlit UI elements */
    #MainMenu, footer, header, .stDeployButton {visibility: hidden; display: none;}
    
    /* Global font */
    * {
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* Page background */
    .stApp {
        background: linear-gradient(135deg, #fff5f0 0%, #ffe0d1 100%) !important;
    }
    
    /* Fix dark bottom area */
    .stApp > div:first-child {
        background: transparent !important;
    }
    
    .stBottom, [data-testid="stBottom"], .stChatFloatingInputContainer {
        background: linear-gradient(135deg, #fff5f0 0%, #ffe0d1 100%) !important;
    }
    
    [data-testid="stBottomBlockContainer"] {
        background: transparent !important;
        padding: 10px 0 20px 0 !important;
    }
    
    /* Chat input wrapper background */
    .stChatInput {
        background: transparent !important;
    }
    
    section[data-testid="stSidebar"], .css-1d391kg, .css-163ttbj {
        background: linear-gradient(135deg, #fff5f0 0%, #ffe0d1 100%) !important;
    }
    
    /* Main container padding */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0 !important;
        max-width: 700px !important;
    }
    
    /* Header styling */
    .chat-header {
        background: linear-gradient(135deg, #ff7e5f, #feb47b);
        padding: 18px 24px;
        border-radius: 20px 20px 0 0;
        display: flex;
        align-items: center;
        gap: 15px;
        color: white;
        box-shadow: 0 4px 15px rgba(255, 126, 95, 0.3);
        margin-bottom: 0;
    }
    
    .chat-header .avatar {
        width: 50px;
        height: 50px;
        background: rgba(255,255,255,0.25);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 26px;
        border: 2px solid rgba(255,255,255,0.5);
    }
    
    .chat-header .info h3 {
        margin: 0;
        font-size: 17px;
        font-weight: 600;
    }
    
    .chat-header .info p {
        margin: 2px 0 0 0;
        font-size: 12px;
        opacity: 0.9;
    }
    
    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        background: #4cd137;
        border-radius: 50%;
        margin-right: 5px;
        border: 1px solid white;
    }
    
    /* Chat container */
    .chat-container {
        background: #fffaf8;
        border-left: 1px solid #ffe0d1;
        border-right: 1px solid #ffe0d1;
        padding: 20px;
        min-height: 400px;
        max-height: 55vh;
        overflow-y: auto;
    }
    
    /* Message bubbles */
    .msg-row {
        display: flex;
        margin-bottom: 16px;
        animation: fadeIn 0.3s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .msg-row.bot {
        justify-content: flex-start;
    }
    
    .msg-row.user {
        justify-content: flex-end;
    }
    
    .msg-bubble {
        max-width: 80%;
        padding: 12px 18px;
        font-size: 14px;
        line-height: 1.6;
        word-wrap: break-word;
    }
    
    .msg-row.bot .msg-bubble {
        background: white;
        color: #333;
        border-radius: 20px 20px 20px 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #f0f0f0;
    }
    
    .msg-row.user .msg-bubble {
        background: linear-gradient(135deg, #ff7e5f, #feb47b);
        color: white;
        border-radius: 20px 20px 4px 20px;
        box-shadow: 0 4px 12px rgba(255, 126, 95, 0.35);
    }
    
    .msg-time {
        font-size: 10px;
        color: #aaa;
        margin-top: 5px;
        padding: 0 5px;
    }
    
    .msg-row.user .msg-time {
        text-align: right;
    }
    
    /* Footer / Input area */
    .chat-footer {
        background: white;
        padding: 15px 20px;
        border-radius: 0 0 20px 20px;
        border: 1px solid #ffe0d1;
        border-top: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    
    /* Override Streamlit chat input */
    .stChatInput {
        background: transparent !important;
    }
    
    .stChatInput > div {
        background: white !important;
        border-radius: 25px !important;
        border: 2px solid #ffe0d1 !important;
        padding: 5px 10px !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important;
    }
    
    .stChatInput > div:focus-within {
        border-color: #feb47b !important;
        background: white !important;
        box-shadow: 0 0 0 3px rgba(255, 126, 95, 0.15) !important;
    }
    
    .stChatInput textarea {
        font-size: 14px !important;
        color: #333 !important;
    }
    
    /* Fix ALL dark areas at bottom */
    .stBottom > div,
    [data-testid="stBottom"] > div,
    .stChatFloatingInputContainer > div,
    [data-testid="stBottomBlockContainer"] > div,
    .css-1p1nwyz,
    .css-1aehpvj,
    .e1f1d6gn0,
    .e1f1d6gn1,
    .e1f1d6gn2 {
        background: transparent !important;
        background-color: transparent !important;
    }
    
    /* Ensure no dark backgrounds anywhere */
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"] {
        background: transparent !important;
    }
    
    /* Typing indicator */
    .typing-indicator {
        display: flex;
        gap: 5px;
        padding: 12px 18px;
        background: white;
        border-radius: 20px 20px 20px 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #f0f0f0;
        width: fit-content;
    }
    
    .typing-indicator span {
        width: 8px;
        height: 8px;
        background: #ff7e5f;
        border-radius: 50%;
        animation: typing 1.4s infinite ease-in-out both;
    }
    
    .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
    .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
    .typing-indicator span:nth-child(3) { animation-delay: 0s; }
    
    @keyframes typing {
        0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }
        40% { transform: scale(1); opacity: 1; }
    }
    
    /* Error box */
    .error-box {
        background: white;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        margin: 20px 0;
    }
    
    .error-box .icon {
        font-size: 40px;
        margin-bottom: 15px;
    }
    
    .error-box h4 {
        color: #ff7e5f;
        margin: 0 0 10px 0;
    }
    
    .error-box p {
        color: #666;
        font-size: 13px;
        margin: 0;
    }
    
    /* Scrollbar */
    .chat-container::-webkit-scrollbar {
        width: 6px;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: rgba(255, 126, 95, 0.3);
        border-radius: 10px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: transparent;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "client" not in st.session_state:
    st.session_state.client = None
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# --- Authentication ---
def get_notebook_client():
    """Try multiple authentication methods."""
    # Method 1: Standard get_client
    try:
        return get_client()
    except Exception:
        pass
    
    # Method 2: Load from cookies.txt
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
    if st.session_state.client:
        st.session_state.authenticated = True

# Hardcoded Notebook ID
TARGET_NOTEBOOK_ID = "8d68d6e7-b095-47ab-b016-a69b7377ad9a"

# --- Helper ---
def get_time():
    return datetime.now().strftime("%H:%M")

# --- UI ---

# Header
st.markdown("""
<div class="chat-header">
    <div class="avatar">🤖</div>
    <div class="info">
        <h3>Chatbot Asisten</h3>
        <p><span class="status-dot"></span>Online</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Check auth
if not st.session_state.authenticated:
    st.markdown("""
    <div class="chat-container">
        <div class="error-box">
            <div class="icon">⚠️</div>
            <h4>Autentikasi Gagal</h4>
            <p>Pastikan file <code>cookies.txt</code> berisi cookies yang valid dari NotebookLM.</p>
        </div>
    </div>
    <div class="chat-footer"></div>
    """, unsafe_allow_html=True)
    st.stop()

# Build chat messages HTML
def render_messages():
    html = '<div class="chat-container">'
    
    # Welcome message if empty
    if not st.session_state.messages:
        html += """
        <div class="msg-row bot">
            <div>
                <div class="msg-bubble">Halo! 👋 Selamat datang. Ada yang bisa saya bantu hari ini?</div>
                <div class="msg-time">{}</div>
            </div>
        </div>
        """.format(get_time())
    
    # Render all messages
    for msg in st.session_state.messages:
        role_class = "bot" if msg["role"] == "assistant" else "user"
        html += f"""
        <div class="msg-row {role_class}">
            <div>
                <div class="msg-bubble">{msg["content"]}</div>
                <div class="msg-time">{msg.get("time", "")}</div>
            </div>
        </div>
        """
    
    html += '</div>'
    return html

# Display chat
st.markdown(render_messages(), unsafe_allow_html=True)

# Footer wrapper
st.markdown('<div class="chat-footer">', unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Ketik pesan...", key="chat_input"):
    current_time = get_time()
    
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "time": current_time
    })
    
    # Get response
    try:
        response = st.session_state.client.query(
            notebook_id=TARGET_NOTEBOOK_ID,
            query_text=prompt
        )
        answer = response.get("answer", "Maaf, saya tidak bisa menjawab saat ini.")
    except Exception as e:
        answer = f"Terjadi kesalahan: {str(e)}"
    
    # Add assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "time": get_time()
    })
    
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
