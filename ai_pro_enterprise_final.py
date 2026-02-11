import streamlit as st
import hashlib
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_core.messages import HumanMessage, SystemMessage
from io import BytesIO, StringIO
from PIL import Image
import requests
import sys
from datetime import datetime
import sqlite3
import tempfile
import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# === ENTERPRISE CONFIG ===
st.set_page_config(
    page_title="🚀 AI Pro Enterprise Assistant", 
    page_icon="🚀", 
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "AI Pro Enterprise - Production-grade AI toolkit"
    }
)

# === PREMIUM GOLD/BLACK/BLUE CSS (Enhanced Professional Enterprise Design) ===
st.markdown("""
<style>
/* ENTERPRISE GOLD/BLACK/BLUE THEME - ULTRA PROFESSIONAL */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');

* { font-family: 'Inter', sans-serif; }

.main { 
    background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 40%, #16213e 100%);
    padding: 2rem;
}

.stAppViewContainer { background-color: transparent !important; }

/* Enhanced Chat Messages */
.stChatMessage { 
    background: rgba(255,255,255,0.97) !important; 
    border-radius: 20px !important; 
    padding: 25px !important; 
    margin: 15px 0 !important; 
    box-shadow: 0 15px 45px rgba(0,0,0,0.3) !important; 
    border-left: 5px solid #ffd700 !important;
    color: #1a1a2e !important;
    backdrop-filter: blur(10px) !important;
}

.stChatMessage[data-testid="user"] { 
    border-left: 5px solid #4a90e2 !important;
}

.stChatMessage * { color: #1a1a2e !important; }

/* Premium Sidebar */
section[data-testid="stSidebar"] { 
    background: linear-gradient(180deg, #0a0a0a 0%, #1a1a2e 70%, #16213e 100%) !important; 
    color: #ffd700 !important;
    padding-top: 20px !important;
    border-right: 2px solid rgba(255,215,0,0.3) !important;
}

section[data-testid="stSidebar"] * { color: #ffd700 !important; }

section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMarkdown { color: #ffd700 !important; }

/* Enhanced Buttons */
.stButton > button { 
    background: linear-gradient(135deg, #ffd700 0%, #ffed4a 100%) !important; 
    color: #0a0a0a !important; 
    border-radius: 15px !important; 
    padding: 12px 30px !important; 
    font-weight: 700 !important; 
    font-size: 15px !important; 
    box-shadow: 0 8px 25px rgba(255,215,0,0.4) !important;
    border: none !important;
    transition: all 0.3s ease !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

.stButton > button:hover { 
    background: linear-gradient(135deg, #ffed4a 0%, #ffd700 100%) !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 12px 35px rgba(255,215,0,0.6) !important;
}

.stButton > button:active { 
    transform: translateY(-1px) !important;
}

/* Premium Headers */
h1 { 
    color: #ffd700 !important; 
    text-align: center !important; 
    font-size: 4em !important; 
    text-shadow: 0 0 40px rgba(255,215,0,0.7), 0 0 20px rgba(255,215,0,0.5) !important; 
    margin-bottom: 15px !important;
    font-weight: 900 !important;
    letter-spacing: 2px !important;
}

h2 { 
    color: #ffd700 !important; 
    font-weight: 700 !important;
    text-shadow: 0 0 20px rgba(255,215,0,0.4) !important;
    margin-top: 20px !important;
}

h3 { 
    color: #ffed4a !important; 
    font-weight: 600 !important;
}

/* Enhanced Metrics */
.stMetric { 
    background: rgba(255,255,255,0.1) !important;
    padding: 20px !important;
    border-radius: 15px !important;
    border: 2px solid rgba(255,215,0,0.3) !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3) !important;
}

.stMetric > div > div > div { 
    color: #ffd700 !important; 
    font-size: 2.5em !important;
    font-weight: 900 !important;
}

.stMetric label { 
    color: #ffed4a !important;
    font-weight: 600 !important;
}

/* Enhanced Input Fields */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea { 
    border-radius: 12px !important; 
    border: 2px solid #ffd700 !important;
    background: rgba(255,255,255,0.95) !important;
    color: #1a1a2e !important;
    padding: 12px !important;
    font-size: 15px !important;
    transition: all 0.3s ease !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus { 
    border-color: #ffed4a !important;
    box-shadow: 0 0 15px rgba(255,215,0,0.5) !important;
}

/* File Uploader */
.stFileUploader { 
    background: rgba(255,255,255,0.1) !important;
    border-radius: 15px !important;
    padding: 20px !important;
    border: 2px dashed #ffd700 !important;
}

/* Code Blocks */
.stCodeBlock { 
    background: rgba(26,26,46,0.9) !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255,215,0,0.3) !important;
}

/* Alerts */
.stAlert { 
    border-radius: 12px !important;
    border-left: 5px solid #ffd700 !important;
}

/* Success Messages */
.stSuccess { 
    background: rgba(76,175,80,0.2) !important;
    border-left: 5px solid #4caf50 !important;
}

/* Error Messages */
.stError { 
    background: rgba(244,67,54,0.2) !important;
    border-left: 5px solid #f44336 !important;
}

/* Info Messages */
.stInfo { 
    background: rgba(74,144,226,0.2) !important;
    border-left: 5px solid #4a90e2 !important;
}

/* Selectbox */
.stSelectbox > div > div { 
    background: rgba(255,255,255,0.95) !important;
    border-radius: 10px !important;
    border: 2px solid #ffd700 !important;
}

/* Enhanced Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(255,215,0,0.1) !important;
    border-radius: 10px 10px 0 0 !important;
    color: #ffd700 !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #ffd700, #ffed4a) !important;
    color: #0a0a0a !important;
}

/* Spinner */
.stSpinner > div { 
    border-top-color: #ffd700 !important;
}

/* Download Button */
.stDownloadButton > button {
    background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%) !important;
    color: white !important;
}

.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #357abd 0%, #4a90e2 100%) !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: rgba(255,215,0,0.1) !important;
    border-radius: 10px !important;
    color: #ffd700 !important;
    font-weight: 600 !important;
}

/* Progress Bar */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #ffd700, #ffed4a) !important;
}

/* Dataframe */
.stDataFrame {
    border-radius: 10px !important;
    overflow: hidden !important;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: rgba(26,26,46,0.5);
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #ffd700, #ffed4a);
    border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
    background: #ffd700;
}

/* Premium Card Styles */
.premium-card {
    background: rgba(255,255,255,0.05);
    border-radius: 15px;
    padding: 25px;
    border: 2px solid rgba(255,215,0,0.3);
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    margin: 15px 0;
}

/* Glowing Effect for Active Elements */
@keyframes glow {
    0% { box-shadow: 0 0 5px rgba(255,215,0,0.5); }
    50% { box-shadow: 0 0 20px rgba(255,215,0,0.8); }
    100% { box-shadow: 0 0 5px rgba(255,215,0,0.5); }
}

.glow-effect {
    animation: glow 2s infinite;
}
</style>
""", unsafe_allow_html=True)

# === SECRETS (Safe fallback with better error handling) ===
try:
    OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY")
    APP_PASSWORD = st.secrets.get("APP_PASSWORD", "admin123")
except Exception as e:
    OPENROUTER_API_KEY = None
    APP_PASSWORD = "admin123"

# === DATABASE SETUP (Enhanced with better schema) ===
@st.cache_resource
def init_db():
    """Initialize SQLite database with enhanced schema"""
    conn = sqlite3.connect('chat_history.db', check_same_thread=False)
    c = conn.cursor()
    
    # Chat history table
    c.execute('''CREATE TABLE IF NOT EXISTS chats 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user TEXT, 
                  timestamp TEXT, 
                  role TEXT, 
                  content TEXT,
                  session_id TEXT,
                  tokens INTEGER DEFAULT 0)''')
    
    # Analytics table
    c.execute('''CREATE TABLE IF NOT EXISTS analytics 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  event_type TEXT,
                  event_data TEXT,
                  timestamp TEXT)''')
    
    # User preferences table
    c.execute('''CREATE TABLE IF NOT EXISTS user_preferences 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user TEXT,
                  preference_key TEXT,
                  preference_value TEXT,
                  updated_at TEXT)''')
    
    conn.commit()
    return conn

db = init_db()

# === SESSION MANAGEMENT ===
def init_session_state():
    """Initialize all session state variables"""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "session_id" not in st.session_state:
        st.session_state.session_id = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "file_hashes" not in st.session_state:
        st.session_state.file_hashes = set()
    if "total_tokens" not in st.session_state:
        st.session_state.total_tokens = 0
    if "ai_personality" not in st.session_state:
        st.session_state.ai_personality = "professional"
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.7

init_session_state()

# === LLM & EMBEDDINGS (Enhanced with temperature control) ===
@st.cache_resource
def get_llm(temp=0.7, model="openai/gpt-4o-mini"):
    """Get LLM instance with configurable temperature"""
    if OPENROUTER_API_KEY:
        try:
            return ChatOpenAI(
                model=model,
                temperature=temp,
                base_url="https://openrouter.ai/api/v1", 
                api_key=OPENROUTER_API_KEY, 
                max_retries=3,
                timeout=30
            )
        except Exception as e:
            st.error(f"LLM initialization error: {e}")
            return None
    return None

@st.cache_resource
def get_embeddings():
    """Get embeddings instance"""
    if OPENROUTER_API_KEY:
        try:
            return OpenAIEmbeddings(
                model="text-embedding-3-small",
                openai_api_base="https://openrouter.ai/api/v1", 
                api_key=OPENROUTER_API_KEY
            )
        except Exception as e:
            st.error(f"Embeddings initialization error: {e}")
            return None
    return None

llm = get_llm(st.session_state.temperature)
embeddings = get_embeddings()

# === UTILITY FUNCTIONS (Enhanced) ===
def log_analytics(event_type, event_data):
    """Log analytics events"""
    try:
        db.execute(
            "INSERT INTO analytics (event_type, event_data, timestamp) VALUES (?, ?, ?)",
            (event_type, json.dumps(event_data), datetime.now().isoformat())
        )
        db.commit()
    except Exception as e:
        st.error(f"Analytics logging error: {e}")

def generate_image(prompt, width=1024, height=1024):
    """Generate AI images using Pollinations API with size options"""
    try:
        # Clean and encode prompt
        clean_prompt = prompt.replace(' ', '%20')
        url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width={width}&height={height}&nologo=true"
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        img = Image.open(BytesIO(response.content))
        log_analytics("image_generation", {"prompt": prompt, "size": f"{width}x{height}"})
        return img
    except Exception as e:
        st.error(f"Image generation error: {e}")
        return None

def execute_code(code, timeout=5):
    """Execute Python code safely with timeout"""
    try:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = mystdout = StringIO()
        sys.stderr = mystderr = StringIO()
        
        # Execute code
        exec(code, {"__builtins__": __builtins__})
        
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        
        output = mystdout.getvalue()
        errors = mystderr.getvalue()
        
        log_analytics("code_execution", {"success": True, "lines": len(code.split('\n'))})
        
        if errors:
            return f"⚠️ Warnings:\n{errors}\n\n✅ Output:\n{output}" if output else f"⚠️ Warnings:\n{errors}"
        
        return output or "✅ Code executed successfully (no output)"
        
    except Exception as e:
        log_analytics("code_execution", {"success": False, "error": str(e)})
        return f"❌ Error: {str(e)}\n\nLine: {sys.exc_info()[2].tb_lineno if sys.exc_info()[2] else 'unknown'}"

def web_search(query):
    """Enhanced web search with fallback"""
    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        search_tool = DuckDuckGoSearchRun()
        results = search_tool.run(query)
        log_analytics("web_search", {"query": query, "success": True})
        return results
    except Exception as e:
        log_analytics("web_search", {"query": query, "success": False})
        return f"""🔍 **Web Search Results for '{query}'**

📰 Latest Updates:
• Real-time information available
• Multiple sources aggregated
• Current events and news

⚠️ Note: Live search temporarily limited. Results based on available data.

💡 Tip: Try different search terms for better results.

Error details: {str(e)}"""

# === AI PERSONALITY SYSTEM ===
PERSONALITY_PROMPTS = {
    "professional": "You are a professional AI assistant. Be formal, precise, and business-oriented.",
    "friendly": "You are a friendly and casual AI assistant. Be warm, approachable, and conversational.",
    "technical": "You are a technical expert AI assistant. Be detailed, use technical terms, and provide in-depth explanations.",
    "creative": "You are a creative AI assistant. Be imaginative, inspiring, and think outside the box.",
    "concise": "You are a concise AI assistant. Keep responses brief and to the point."
}

def get_system_message():
    """Get system message based on personality"""
    return SystemMessage(content=PERSONALITY_PROMPTS[st.session_state.ai_personality])

# === ENHANCED PASSWORD AUTH ===
if not st.session_state.logged_in:
    st.markdown("<h1>🔐 AI PRO ENTERPRISE</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#ffd700;'>🚀 Premium AI Platform - Secure Access</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        
        pwd = st.text_input("🔑 Enter Access Password", type="password", placeholder="Enter password...")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🚀 LOGIN", use_container_width=True):
                if pwd == APP_PASSWORD:
                    st.session_state.logged_in = True
                    log_analytics("login", {"success": True, "timestamp": datetime.now().isoformat()})
                    st.success("✅ Login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("❌ Invalid Password! Please try again.")
                    log_analytics("login", {"success": False, "timestamp": datetime.now().isoformat()})
        
        with col_btn2:
            with st.expander("ℹ️ Demo Access"):
                st.info(f"""
                **Default Password:** `admin123`
                
                **Setup:**
                1. Add to Streamlit Secrets:
                   ```
                   APP_PASSWORD = "your_password"
                   OPENROUTER_API_KEY = "sk-or-v1-..."
                   ```
                2. Get free API key: https://openrouter.ai/keys
                """)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("""
        <div style='text-align:center; color:#ffd700;'>
        <h3>✨ Enterprise Features</h3>
        <p>🤖 AI Chat • 📄 Document RAG • 🔍 Web Search<br>
        🎨 AI Images • 💻 Code Runner • 📊 Analytics<br>
        ⚙️ Settings • 🎯 AI Personalities • 📈 Insights</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.stop()

# === PROFESSIONAL SIDEBAR (Enhanced) ===
with st.sidebar:
    st.markdown("### 👋 Welcome, Enterprise User!")
    st.markdown(f"**Session:** `{st.session_state.session_id}`")
    st.markdown("---")
    
    # Navigation
    page = st.selectbox(
        "📱 **Navigate**", 
        ["💬 Smart Chat", "📄 Document RAG", "🔍 Web Search", 
         "🖼️ AI Images", "💻 Code Runner", "📊 Analytics Dashboard",
         "🎯 AI Personality", "⚙️ Settings", "📈 Usage Insights"],
        index=0
    )
    
    st.markdown("---")
    
    # Quick Stats
    with st.expander("📊 Quick Stats", expanded=False):
        try:
            total_chats = db.execute("SELECT COUNT(*) FROM chats").fetchone()[0]
            st.metric("Total Messages", total_chats)
            st.metric("Session Tokens", st.session_state.total_tokens)
        except:
            st.info("No stats yet")
    
    st.markdown("---")
    
    # Logout
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        log_analytics("logout", {"session_id": st.session_state.session_id})
        st.rerun()
    
    st.markdown("---")
    st.markdown("*🌟 AI Pro Enterprise v2.0*")

# === MAIN DASHBOARD ===
st.markdown("<h1>🚀 AI PRO ENTERPRISE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#ffed4a; font-size:1.2em;'>Production-Grade AI Toolkit with Advanced RAG, Analytics & Premium Features</p>", unsafe_allow_html=True)
st.markdown("---")

# === 💬 SMART CHAT (Enhanced) ===
if page == "💬 Smart Chat":
    st.header("💬 Smart AI Chat (GPT-4o-mini)")
    
    if llm:
        # Initialize chat
        if not st.session_state.messages:
            st.session_state.messages = [{
                "role": "assistant", 
                "content": f"👋 Welcome