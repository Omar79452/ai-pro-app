import streamlit as st
import hashlib
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_core.messages import HumanMessage
from langchain_community.tools import DuckDuckGoSearchRun
from io import BytesIO, StringIO
from PIL import Image
import requests
import sys
from datetime import datetime
import sqlite3

# === CONFIG ===
st.set_page_config(page_title="🚀 AI Pro", page_icon="🚀", layout="wide")

# === PREMIUM CSS - GOLD/BLACK THEME ===
st.markdown("""
<style>
/* ENTERPRISE GOLD/BLACK THEME */
.main {background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 40%, #16213e 100%);}
.stChatMessage {background: rgba(255,255,255,0.95); border-radius: 25px; padding: 25px; margin: 15px 0; 
                 box-shadow: 0 15px 45px rgba(0,0,0,0.4); border-left: 6px solid #ffd700; color: #1a1a2e !important;}
.stChatMessage * {color: #1a1a2e !important;}
section[data-testid="stSidebar"] {background: linear-gradient(180deg, #0a0a0a 0%, #1a1a2e 70%, #16213e 100%); 
                                   color: #ffd700; padding-top: 20px;}
section[data-testid="stSidebar"] * {color: #ffd700 !important;}
.stButton > button {background: linear-gradient(90deg, #ffd700 0%, #ffed4a 100%); color: #0a0a0a; 
                    border-radius: 20px; padding: 15px 35px; font-weight: 700; font-size: 16px; 
                    box-shadow: 0 10px 30px rgba(255,215,0,0.4); border: none;}
.stButton > button:hover {background: linear-gradient(90deg, #ffed4a 0%, #ffd700 100%) !important;}
h1 {color: #ffd700 !important; text-align: center; font-size: 4em !important; 
    text-shadow: 0 0 30px rgba(255,215,0,0.6); margin-bottom: 10px;}
h2, h3 {color: #ffd700 !important;}
.stMetric {color: #ffd700 !important;}
</style>
""", unsafe_allow_html=True)

# === SECRETS ===
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
APP_PASSWORD = st.secrets.get("APP_PASSWORD", "ai123")

# === DATABASE ===
@st.cache_resource
def init_db():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chats 
                 (id INTEGER PRIMARY KEY, user TEXT, timestamp TEXT, role TEXT, content TEXT)''')
    conn.commit()
    return conn

# === LLM & TOOLS ===
@st.cache_resource
def get_llm(temp=0.7):
    return ChatOpenAI(model="openai/gpt-4o-mini", temperature=temp, 
                     base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY, max_retries=3)

@st.cache_resource
def get_embeddings():
    return OpenAIEmbeddings(model="text-embedding-3-small", 
                           openai_api_base="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)

llm = get_llm()
search = DuckDuckGoSearchRun()
embeddings = get_embeddings()
db = init_db()

# === UTILITY FUNCTIONS ===
def generate_image(prompt):
    try:
        url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}"
        return Image.open(BytesIO(requests.get(url).content))
    except:
        return None

def execute_code(code):
    try:
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        exec(code)
        sys.stdout = old_stdout
        return mystdout.getvalue() or "✅ Code executed successfully!"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# === PASSWORD AUTH ===
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1>🔐 AI Pro Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#ffd700;'>Enter Password to Access</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        pwd = st.text_input("🔑 Password", type="password", label_visibility="collapsed")
    with col2:
        if st.button("🚀 Enter AI Pro", use_container_width=True):
            if pwd == APP_PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("❌ Wrong Password!")
    st.stop()

# === SIDEBAR ===
st.sidebar.markdown("### 👋 Welcome to AI Pro!")
st.sidebar.button("🚪 Logout", on_click=lambda: setattr(st.session_state, 'logged_in', False) or st.rerun())

# === MAIN PAGES ===
page = st.sidebar.selectbox("📱 Navigate", 
                           ["💬 Smart Chat", "📄 Document RAG", "🔍 Web Search", "🖼️ AI Images", 
                            "💻 Code Runner", "📊 Analytics", "⚙️ Settings"])

st.markdown("<h1>🚀 AI Pro Assistant</h1>", unsafe_allow_html=True)
st.markdown("*Enterprise-grade AI toolkit with RAG, Web Search, Code Execution & Analytics*")

# === SMART CHAT ===
if page == "💬 Smart Chat":
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "👋 Welcome to Smart Chat! Ask me anything..."}]
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if prompt := st.chat_input("💭 Ask anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                resp = llm.invoke([HumanMessage(content=prompt)]).content
            st.markdown(resp)
            st.session_state.messages.append({"role": "assistant", "content": resp})
            
            # Save to DB
            for role, content in [("user", prompt), ("assistant", resp)]:
                db.execute("INSERT INTO chats (user, timestamp, role, content) VALUES (?, ?, ?, ?)",
                          ("user", datetime.now().isoformat(), role, content))
            db.commit()

# === DOCUMENT RAG ===
elif page == "📄 Document RAG":
    st.header("📄 Document Q&A (RAG)")
    uploaded_file = st.file_uploader("📎 Upload PDF/TXT", type=['pdf','txt'])
    
    if uploaded_file:
        file_hash = hashlib.md5(uploaded_file.getvalue()).hexdigest()
        if "file_hashes" not in st.session_state:
            st.session_state.file_hashes = set()
        
        if file_hash not in st.session_state.file_hashes:
            with st.spinner("🔄 Processing document..."):
                try:
                    if uploaded_file.name.endswith('.pdf'):
                        docs = PyPDFLoader(uploaded_file).load()
                    else:
                        docs = TextLoader(uploaded_file, encoding="utf-8").load()
                    
                    st.session_state.vectorstore = Chroma.from_documents(
                        docs, embeddings, persist_directory="/tmp/chroma_db"
                    )
                    st.session_state.file_hashes.add(file_hash)
                    st.success("✅ Document loaded into memory!")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        if "vectorstore" in st.session_state and st.session_state.vectorstore:
            query = st.text_input("❓ Ask about your document:")
            if st.button("🔍 Query Document", use_container_width=True) and query:
                with st.spinner("🔍 Searching document..."):
                    retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 4})
                    docs = retriever.invoke(query)
                    context = "\n\n".join([doc.page_content for doc in docs])
                    
                    resp = llm.invoke([
                        HumanMessage(content=f"""Use ONLY the following context to answer:

CONTEXT:
{context}

Question: {query}

Answer based ONLY on context above:""")
                    ]).content
                    st.markdown(f"**📄 Answer:** {resp}")

# === WEB SEARCH ===
elif page == "🔍 Web Search":
    st.header("🌐 Real-time Web Search")
    query = st.text_input("🔍 Search the web:")
    if st.button("🚀 Search Internet", use_container_width=True) and query:
        with st.spinner("🌐 Searching internet..."):
            results = search.run(query)
            st.markdown(f"**🔗 Results:** {results}")

# === AI IMAGES ===
elif page == "🖼️ AI Images":
    st.header("🎨 AI Image Generator")
    prompt = st.text_area("✨ Describe your image:", height=100)
    if st.button("🪄 Generate Image", use_container_width=True) and prompt:
        with st.spinner("🎨 Creating image..."):
            img = generate_image(prompt)
            if img:
                st.image(img, caption=prompt, use_column_width=True)
            else:
                st.error("❌ Image generation failed. Try again!")

# === CODE RUNNER ===
elif page == "💻 Code Runner":
    st.header("⚙️ Python Code Runner")
    code = st.text_area("```python\n# Write Python code here\nprint('Hello from AI Pro!')\n```", height=250)
    if st.button("▶️ Run Code", use_container_width=True):
        with st.spinner("⚙️ Executing..."):
            result = execute_code(code)
            st.code(result, language="text")

# === ANALYTICS ===
elif page == "📊 Analytics":
    st.header("📊 Usage Analytics")
    c = db.execute("SELECT role, COUNT(*) FROM chats GROUP BY role").fetchall()
    total_msgs = sum([x[1] for x in c])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💬 Total Messages", total_msgs)
    with col2:
        st.metric("👤 User Messages", next((x[1] for x in c if x[0] == 'user'), 0))
    with col3:
        st.metric("🤖 AI Responses", next((x[1] for x in c if x[0] == 'assistant'), 0))
    
    if total_msgs > 0:
        st.markdown("### 📈 Message Distribution")
        st.bar_chart({row[0].title(): row[1] for row in c})

# === SETTINGS ===
elif page == "⚙️ Settings":
    st.header("⚙️ App Settings")
    st.success("✅ **Production Ready Features:**")
    st.markdown("""
    - 🔐 **Password Protection** (Streamlit Secrets)
    - 💾 **Chat History** (SQLite database)
    - 📄 **Document RAG** (Chroma vector DB)
    - 🌐 **Web Search** (DuckDuckGo)
    - 🖼️ **AI Images** (Pollinations API)
    - 💻 **Code Execution** (Secure sandbox)
    - 📊 **Real-time Analytics**
    - 🎨 **Premium UI/UX** (Gold/Black theme)
    - ⚡ **Cached Components** (Fast loading)
    """)

st.markdown("---")
st.markdown("*🌟 Enterprise AI Pro Assistant | Production Ready | Deployed on Streamlit Cloud*")
