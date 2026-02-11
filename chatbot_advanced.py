import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import os

# Optional analytics
try:
    import pandas as pd
    import plotly.express as px
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False

# LangChain
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="AI Pro Enterprise",
    page_icon="🚀",
    layout="wide"
)

# Clean dark theme
st.markdown("""
<style>
.stApp { background-color: #0f172a; color: #e2e8f0; }
section[data-testid="stSidebar"] { background-color: #111827; }
.stChatMessage { 
    background-color: #1e293b !important;
    border-radius: 10px !important;
    padding: 15px !important;
}
.stChatMessage[data-testid="user"] {
    background-color: #2563eb !important;
    color: white !important;
}
.stButton > button {
    background-color: #2563eb !important;
    color: white !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# SECRETS
# =====================================================

OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
APP_PASSWORD = st.secrets.get("APP_PASSWORD", "admin123")

# =====================================================
# DATABASE
# =====================================================

@st.cache_resource
def init_db():
    try:
        conn = sqlite3.connect("ai_pro.db", check_same_thread=False)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY,
                session_id TEXT,
                role TEXT,
                content TEXT,
                timestamp TEXT
            )
        """)
        conn.commit()
        return conn
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return None

db = init_db()

# =====================================================
# SESSION INIT
# =====================================================

def init_session():
    defaults = {
        "logged_in": False,
        "session_id": hashlib.md5(str(datetime.now()).encode()).hexdigest()[:10],
        "messages": [],
        "model_name": "openai/gpt-4o-mini",
        "temperature": 0.7
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# =====================================================
# LOAD CHAT HISTORY FROM DB
# =====================================================

def load_history():
    try:
        cursor = db.execute(
            "SELECT role, content FROM chats WHERE session_id=? ORDER BY id",
            (st.session_state.session_id,)
        )
        rows = cursor.fetchall()
        st.session_state.messages = [
            {"role": r[0], "content": r[1]} for r in rows
        ]
    except sqlite3.Error as e:
        st.error(f"Error loading chat history: {e}")

if not st.session_state.messages:
    load_history()

def save_message(role, content):
    try:
        db.execute(
            "INSERT INTO chats (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
            (
                st.session_state.session_id,
                role,
                content,
                datetime.now().isoformat()
            )
        )
        db.commit()
    except sqlite3.Error as e:
        st.error(f"Error saving message: {e}")

# =====================================================
# LLM INIT
# =====================================================

llm = None
if LANGCHAIN_AVAILABLE and OPENROUTER_API_KEY:
    try:
        llm = ChatOpenAI(
            model=st.session_state.model_name,
            temperature=st.session_state.temperature,
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
            max_retries=2
        )
    except Exception as e:
        st.error(f"LLM init error: {e}")

# =====================================================
# LOGIN
# =====================================================

if not st.session_state.logged_in:
    st.title("AI Pro Enterprise")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if pwd == APP_PASSWORD:
            st.session_state.logged_in = True
            st.success("Login successful!")
            st.experimental_rerun()
        else:
            st.error("Invalid password")

    st.stop()

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:
    st.header("Control Panel")

    page = st.radio("Navigation", [
        "Chat",
        "Analytics",
        "Settings"
    ])

    st.divider()

    st.write("Session:", st.session_state.session_id)
    st.write("Messages:", len(st.session_state.messages))

    if st.button("Clear Chat"):
        db.execute(
            "DELETE FROM chats WHERE session_id=?",
            (st.session_state.session_id,)
        )
        db.commit()
        st.session_state.messages = []
        st.success("Chat cleared!")
        st.experimental_rerun()

    if st.button("Logout"):
        st.session_state.clear()
        st.success("Logged out successfully!")
        st.experimental_rerun()

# =====================================================
# MAIN
# =====================================================

st.title("🚀 AI Pro Enterprise")

# =====================================================
# CHAT
# =====================================================

if page == "Chat":

    if not llm:
        st.warning("Set OPENROUTER_API_KEY in Streamlit secrets.")
        st.stop()

    # Display history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # New input
    if prompt := st.chat_input("Ask something..."):

        st.session_state.messages.append({"role": "user", "content": prompt})
        save_message("user", prompt)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""

            try:
                messages = [SystemMessage(content="You are a professional AI assistant.")]

                for m in st.session_state.messages[-8:]:
                    if m["role"] == "user":
                        messages.append(HumanMessage(content=m["content"]))
                    else:
                        messages.append(AIMessage(content=m["content"]))

                for chunk in llm.stream(messages):
                    full_response += chunk.content or ""
                    placeholder.markdown(full_response + "▌")

                placeholder.markdown(full_response)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response
                })

                save_message("assistant", full_response)

            except Exception as e:
                placeholder.markdown(f"Error: {e}")

# =====================================================
# ANALYTICS
# =====================================================

elif page == "Analytics":

    st.header("Usage Analytics")

    try:
        cursor = db.execute("""
            SELECT DATE(timestamp) as day, COUNT(*) 
            FROM chats 
            GROUP BY day
            ORDER BY day
        """)

        rows = cursor.fetchall()

        if rows and ANALYTICS_AVAILABLE:
            df = pd.DataFrame(rows, columns=["Date", "Messages"])
            fig = px.line(df, x="Date", y="Messages", title="Messages per Day")
            st.plotly_chart(fig, use_container_width=True)
        elif rows:
            st.write(rows)
        else:
            st.info("No data yet.")
    except sqlite3.Error as e:
        st.error(f"Error fetching analytics data: {e}")

# =====================================================
# SETTINGS
# =====================================================

elif page == "Settings":

    st.header("Model Settings")

    st.session_state.model_name = st.selectbox(
        "Model",
        ["openai/gpt-4o-mini", "openai/gpt-4o"]
    )

    st.session_state.temperature = st.slider(
        "Temperature",
        0.0,
        1.0,
        st.session_state.temperature
    )

    st.info("Restart app after changing API key.")