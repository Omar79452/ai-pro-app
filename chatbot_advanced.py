import streamlit as st
import hashlib
import sqlite3
from datetime import datetime
from io import BytesIO
from PIL import Image
import requests
import sys
import os
import json
import time

# Optional deps
PLOTLY_AVAILABLE = False
PANDAS_AVAILABLE = False
try:
    import pandas as pd
    import plotly.express as px
    PLOTLY_AVAILABLE = True
    PANDAS_AVAILABLE = True
except ImportError:
    pass

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


# ==============================
# PAGE CONFIG
# ==============================

st.set_page_config(
    page_title="AI Pro Enterprise",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================
# CLEAN PROFESSIONAL DARK THEME
# ==============================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}

/* Main background */
.stApp {
    background-color: #0f172a;
    color: #e2e8f0;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #111827;
    border-right: 1px solid #1f2937;
}

/* Headers */
h1, h2, h3 {
    color: #f8fafc !important;
    font-weight: 600 !important;
}

/* Cards */
.card {
    background-color: #111827;
    padding: 24px;
    border-radius: 12px;
    border: 1px solid #1f2937;
    margin-bottom: 20px;
}

/* Chat messages */
.stChatMessage {
    background-color: #1e293b !important;
    border-radius: 12px !important;
    padding: 16px !important;
    border: 1px solid #334155 !important;
    color: #e2e8f0 !important;
}

.stChatMessage[data-testid="user"] {
    background-color: #1d4ed8 !important;
    color: white !important;
    border: none !important;
}

/* Buttons */
.stButton > button {
    background-color: #2563eb !important;
    color: white !important;
    border-radius: 8px !important;
    border: none !important;
    padding: 10px 18px !important;
    font-weight: 500 !important;
}

.stButton > button:hover {
    background-color: #1d4ed8 !important;
}

/* Inputs */
input, textarea {
    background-color: #1e293b !important;
    color: white !important;
}

</style>
""", unsafe_allow_html=True)


# ==============================
# SECRETS
# ==============================

try:
    OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
    APP_PASSWORD = st.secrets.get("APP_PASSWORD", "admin123")
except:
    OPENROUTER_API_KEY = ""
    APP_PASSWORD = "admin123"


# ==============================
# DATABASE
# ==============================

@st.cache_resource
def init_db():
    conn = sqlite3.connect("ai_pro.db", check_same_thread=False)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY,
            session_id TEXT,
            role TEXT,
            content TEXT,
            tokens INTEGER,
            timestamp TEXT
        )
    """)

    conn.commit()
    return conn

db = init_db()


# ==============================
# SESSION INIT
# ==============================

def init_session():
    defaults = {
        "logged_in": False,
        "session_id": hashlib.md5(str(datetime.now()).encode()).hexdigest()[:10],
        "messages": [],
        "total_tokens": 0,
        "temperature": 0.7,
        "model_name": "openai/gpt-4o-mini",
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# ==============================
# LLM INIT
# ==============================

llm = None
if LANGCHAIN_AVAILABLE and OPENROUTER_API_KEY:
    try:
        llm = ChatOpenAI(
            model=st.session_state.model_name,
            temperature=st.session_state.temperature,
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )
    except Exception as e:
        st.error(str(e))


# ==============================
# LOGIN
# ==============================

if not st.session_state.logged_in:

    st.markdown("<h1 style='text-align:center;'>AI Pro Enterprise</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#94a3b8;'>Secure Access Required</p>", unsafe_allow_html=True)

    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if pwd == APP_PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid password")

    st.stop()


# ==============================
# SIDEBAR
# ==============================

with st.sidebar:
    st.markdown("### Control Panel")
    st.markdown(f"Session: `{st.session_state.session_id}`")

    page = st.radio("Navigation", [
        "Chat",
        "Analytics",
        "Settings"
    ])

    st.divider()

    st.metric("Messages", len(st.session_state.messages))
    st.metric("Tokens", st.session_state.total_tokens)

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    if st.button("Logout"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


# ==============================
# MAIN
# ==============================

st.title("AI Pro Enterprise")


# ==============================
# CHAT PAGE
# ==============================

if page == "Chat":

    if llm:

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask something..."):

            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                placeholder = st.empty()
                full = ""

                try:
                    messages = [SystemMessage(content="You are a professional AI assistant.")]

                    for m in st.session_state.messages[-8:]:
                        if m["role"] == "user":
                            messages.append(HumanMessage(content=m["content"]))
                        else:
                            messages.append(AIMessage(content=m["content"]))

                    for chunk in llm.stream(messages):
                        full += chunk.content or ""
                        placeholder.markdown(full + "▌")

                    placeholder.markdown(full)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": full
                    })

                    st.session_state.total_tokens += len(full.split())

                except Exception as e:
                    placeholder.markdown(f"Error: {e}")

    else:
        st.warning("Add OPENROUTER_API_KEY to Streamlit secrets.")


# ==============================
# ANALYTICS
# ==============================

elif page == "Analytics":

    st.header("Usage Analytics")

    if PLOTLY_AVAILABLE and PANDAS_AVAILABLE:

        df = pd.DataFrame({
            "Day": list(range(1, 31)),
            "Messages": [len(st.session_state.messages) + i for i in range(30)]
        })

        fig = px.line(df, x="Day", y="Messages", title="Message Growth")
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Install pandas + plotly for charts.")


# ==============================
# SETTINGS
# ==============================

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

    st.info("Restart app after changing secrets.")


# ==============================
# FOOTER
# ==============================

st.divider()
st.caption("AI Pro Enterprise — Production Ready")
