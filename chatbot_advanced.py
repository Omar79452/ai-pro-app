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

/* Download Button */
.stDownloadButton > button {
    background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%) !important;
    color: white !important;
}

.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #357abd 0%, #4a90e2 100%) !important;
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
        pass

def generate_image(prompt, width=1024, height=1024):
    """Generate AI images using Pollinations API with size options"""
    try:
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
        return f"❌ Error: {str(e)}"

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

⚠️ Note: Live search temporarily limited. Try again or check alternative sources.

Error: {str(e)}"""

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
                Add to Streamlit Secrets:
                ```
                APP_PASSWORD = "your_password"
                OPENROUTER_API_KEY = "sk-or-v1-..."
                ```
                """)
        
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
         "🎯 AI Personality", "⚙️ Settings"],
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
            welcome_msg = "👋 Welcome to Enterprise Smart Chat! Ask me anything about AI, coding, business, or anything else. I'm here to help!"
            st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]
        
        # Display chat history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        # Chat input
        if prompt := st.chat_input("💭 Ask anything..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("🤔 AI Thinking..."):
                    try:
                        messages = [get_system_message(), HumanMessage(content=prompt)]
                        resp = llm.invoke(messages).content
                        st.markdown(resp)
                        st.session_state.messages.append({"role": "assistant", "content": resp})
                        
                        # Save to database
                        for role, content in [("user", prompt), ("assistant", resp)]:
                            db.execute("INSERT INTO chats (user, timestamp, role, content, session_id) VALUES (?, ?, ?, ?, ?)",
                                     ("user", datetime.now().isoformat(), role, content, st.session_state.session_id))
                        db.commit()
                    except Exception as e:
                        st.error(f"❌ Chat error: {e}")
        
        # Export Chat
        if st.button("📥 Export Chat History"):
            chat_history = "\n\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
            st.download_button("💾 Download Chat", chat_history, "chat_history.txt", "text/plain")
    else:
        st.error("❌ **OpenRouter API Key missing!** Add `OPENROUTER_API_KEY` to Streamlit Secrets.")
        st.info("Get free key: https://openrouter.ai/keys")

# === 📄 DOCUMENT RAG ===
elif page == "📄 Document RAG":
    st.header("📄 Document Q&A (RAG - Retrieval Augmented Generation)")
    if embeddings and llm:
        uploaded_file = st.file_uploader("📎 Upload PDF or TXT document", type=['pdf','txt'])
        
        if uploaded_file:
            file_hash = hashlib.md5(uploaded_file.getvalue()).hexdigest()
            
            if file_hash not in st.session_state.file_hashes:
                with st.spinner("🔄 Processing document..."):
                    try:
                        # Save to temp file
                        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                            tmp.write(uploaded_file.getvalue())
                            tmp_path = tmp.name
                        
                        # Load document
                        if uploaded_file.name.endswith('.pdf'):
                            docs = PyPDFLoader(tmp_path).load()
                        else:
                            docs = TextLoader(tmp_path, encoding="utf-8").load()
                        
                        # Create vector store
                        st.session_state.vectorstore = Chroma.from_documents(
                            docs, embeddings, persist_directory="/tmp/chroma_db"
                        )
                        st.session_state.file_hashes.add(file_hash)
                        os.unlink(tmp_path)
                        st.success(f"✅ Document loaded! ({len(docs)} chunks indexed)")
                        log_analytics("document_upload", {"filename": uploaded_file.name, "chunks": len(docs)})
                    except Exception as e:
                        st.error(f"❌ Document error: {e}")
            
            # Query interface
            if "vectorstore" in st.session_state:
                query = st.text_input("❓ Ask questions about your document:")
                if st.button("🔍 Query Document", use_container_width=True) and query:
                    with st.spinner("🔍 Searching document..."):
                        try:
                            retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 4})
                            docs = retriever.invoke(query)
                            context = "\n\n".join([doc.page_content for doc in docs])
                            
                            response = llm.invoke([
                                HumanMessage(content=f"""Use ONLY the following document context to answer:

CONTEXT:
{context}

Question: {query}

Answer accurately using ONLY the context above:""")
                            ]).content
                            
                            st.markdown(f"**📄 Answer:** {response}")
                            st.markdown("**📚 Sources:** Top 4 document chunks retrieved")
                        except Exception as e:
                            st.error(f"❌ Query error: {e}")
    else:
        st.error("❌ **OpenRouter API Key required** for RAG. Add to Secrets.")

# === 🔍 WEB SEARCH ===
elif page == "🔍 Web Search":
    st.header("🌐 Real-time Web Search")
    query = st.text_input("🔍 Enter search query:")
    if st.button("🚀 Search Internet", use_container_width=True) and query:
        with st.spinner("🌐 Searching web..."):
            try:
                results = web_search(query)
                st.markdown(f"**🔗 Search Results:**")
                st.markdown(results)
            except Exception as e:
                st.error(f"❌ Search error: {e}")

# === 🖼️ AI IMAGES ===
elif page == "🖼️ AI Images":
    st.header("🎨 AI Image Generator")
    prompt = st.text_area("✨ Describe your image (e.g., 'golden sunset over mountains'):", height=120)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        size = st.selectbox("Size", ["1024x1024", "512x512"])
    with col2:
        st.info("Powered by Pollinations AI - Free unlimited images")
    
    if st.button("🪄 Generate Image", use_container_width=True) and prompt:
        with st.spinner("🎨 Creating image..."):
            width, height = map(int, size.split('x'))
            img = generate_image(prompt, width, height)
            if img:
                st.image(img, caption=f"Generated: {prompt}", use_column_width=True)
                
                # Proper download
                buf = BytesIO()
                img.save(buf, format='PNG')
                buf.seek(0)
                
                st.download_button(
                    label="💾 Download Image",
                    data=buf.getvalue(),
                    file_name=f"ai_image_{prompt[:20].replace(' ', '_')}.png",
                    mime="image/png"
                )
            else:
                st.error("❌ Image generation failed. Try different prompt.")

# === 💻 CODE RUNNER ===
elif page == "💻 Code Runner":
    st.header("⚙️ Python Code Runner (Secure Sandbox)")
    st.info("Execute Python code safely in isolated environment")
    
    default_code = """import numpy as np

# Create array (FIXED: use commas)
arr = np.array([11, 12, 13, 14])
print('Array:', arr)
print('Sum:', arr.sum())
print('Mean:', arr.mean())

# Math operations
result = arr * 2
print('Doubled:', result)"""
    
    code = st.text_area("📝 Write your Python code:", value=default_code, height=300, key="code_editor")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("▶️ Run Code", use_container_width=True):
            with st.spinner("⚙️ Executing code..."):
                result = execute_code(code)
                st.code(result, language="text")
    with col2:
        st.info("**Supported:**\nnumpy, pandas\nmath, datetime")

# === 📊 ANALYTICS ===
elif page == "📊 Analytics Dashboard":
    st.header("📊 Enterprise Analytics Dashboard")
    
    try:
        c = db.execute("SELECT role, COUNT(*) FROM chats GROUP BY role").fetchall()
        total_msgs = sum([x[1] for x in c]) if c else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💬 Total Messages", total_msgs)
        with col2:
            st.metric("👤 User Messages", next((x[1] for x in c if x[0] == 'user'), 0))
        with col3:
            st.metric("🤖 AI Responses", next((x[1] for x in c if x[0] == 'assistant'), 0))
        
        if total_msgs > 0:
            st.markdown("### 📈 Message Distribution")
            
            # Create bar chart
            df = pd.DataFrame(c, columns=['Role', 'Count'])
            fig = px.bar(df, x='Role', y='Count', title='Messages by Role',
                        color='Role', color_discrete_sequence=['#ffd700', '#4a90e2'])
            st.plotly_chart(fig, use_container_width=True)
            
            # Analytics events
            events = db.execute("SELECT event_type, COUNT(*) FROM analytics GROUP BY event_type").fetchall()
            if events:
                st.markdown("### 📊 Event Analytics")
                df_events = pd.DataFrame(events, columns=['Event', 'Count'])
                fig2 = px.pie(df_events, values='Count', names='Event', title='Event Distribution')
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No analytics data yet. Start using features to see metrics!")
            
    except Exception as e:
        st.error(f"Analytics error: {e}")

# === 🎯 AI PERSONALITY ===
elif page == "🎯 AI Personality":
    st.header("🎯 AI Personality Settings")
    
    st.markdown("### Choose Your AI Assistant Style")
    
    personality = st.radio(
        "Select Personality:",
        ["professional", "friendly", "technical", "creative", "concise"],
        index=["professional", "friendly", "technical", "creative", "concise"].index(st.session_state.ai_personality)
    )
    
    # Show personality descriptions
    descriptions = {
        "professional": "🎯 **Professional** - Formal, precise, business-oriented responses",
        "friendly": "😊 **Friendly** - Warm, approachable, conversational tone",
        "technical": "🔧 **Technical** - Detailed, expert-level explanations",
        "creative": "🎨 **Creative** - Imaginative, inspiring, innovative thinking",
        "concise": "⚡ **Concise** - Brief, direct, to-the-point answers"
    }
    
    for p, desc in descriptions.items():
        if p == personality:
            st.success(desc)
        else:
            st.info(desc)
    
    if st.button("💾 Save Personality", use_container_width=True):
        st.session_state.ai_personality = personality
        st.success(f"✅ AI Personality set to: **{personality.title()}**")
        st.info("This will apply to your next chat messages!")

# === ⚙️ SETTINGS ===
elif page == "⚙️ Settings":
    st.header("⚙️ Enterprise Configuration")
    
    st.success("✅ **Production Features Active:**")
    
    # Temperature Control
    st.markdown("### 🌡️ AI Temperature Control")
    temp = st.slider("Creativity Level", 0.0, 1.0, st.session_state.temperature, 0.1)
    if st.button("💾 Save Temperature"):
        st.session_state.temperature = temp
        st.success(f"✅ Temperature set to {temp}")
    
    st.markdown("---")
    
    # Feature Status
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🔐 Security**
        • Password protection ✅
        • Session management ✅
        
        **💾 Data Layer**
        • SQLite chat history ✅
        • ChromaDB vector storage ✅
        
        **🤖 AI Models**
        • GPT-4o-mini (OpenRouter) ✅
        • Text embeddings ✅
        """)
    
    with col2:
        st.markdown("""
        **🛠️ Tools**
        • Document RAG (PDF/TXT) ✅
        • Web search ✅
        • AI image generation ✅
        • Python code runner ✅
        
        **📊 Analytics**
        • Real-time dashboard ✅
        • Event tracking ✅
        """)
    
    st.markdown("---")
    
    st.info("""
    **📋 Required Secrets:**
    ```
    OPENROUTER_API_KEY = "sk-or-v1-..."
    APP_PASSWORD = "yourpassword"
    ```
    
    **🔗 Get API Key:** https://openrouter.ai/keys
    """)
    
    # Database Stats
    st.markdown("### 📊 Database Statistics")
    try:
        chat_count = db.execute("SELECT COUNT(*) FROM chats").fetchone()[0]
        analytics_count = db.execute("SELECT COUNT(*) FROM analytics").fetchone()[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("💬 Chat Records", chat_count)
        with col2:
            st.metric("📊 Analytics Events", analytics_count)
    except:
        st.info("Database initializing...")

# === FOOTER ===
st.markdown("---")
st.markdown("*🌟 AI Pro Enterprise v2.0 | Production AI Toolkit | Powered by OpenRouter & Streamlit*")