import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import json

# Optional analytics
try:
    import pandas as pd
    import plotly.express as px
    ANALYTICS_AVAILABLE = True
except:
    ANALYTICS_AVAILABLE = False

# LangChain
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    from langchain_core.callbacks import BaseCallbackHandler
    LANGCHAIN_AVAILABLE = True
except:
    LANGCHAIN_AVAILABLE = False


# =====================================================
# CONFIG
# =====================================================

st.set_page_config(page_title="AI Pro Enterprise+", layout="wide")

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
    conn = sqlite3.connect("ai_pro_plus.db", check_same_thread=False)
    conn.execute("""
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


# =====================================================
# SESSION INIT
# =====================================================

def init_session():
    defaults = {
        "logged_in": False,
        "session_id": hashlib.md5(str(datetime.now()).encode()).hexdigest()[:10],
        "messages": [],
        "model_name": "openai/gpt-4o-mini",
        "temperature": 0.7,
        "system_prompt": "You are a professional AI assistant.",
        "context_window": 8,
        "total_tokens": 0
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# =====================================================
# TOKEN CALLBACK
# =====================================================

class TokenCounter(BaseCallbackHandler):
    def __init__(self):
        self.total_tokens = 0

    def on_llm_end(self, response, **kwargs):
        try:
            self.total_tokens += response.llm_output["token_usage"]["total_tokens"]
        except:
            pass


# =====================================================
# DB FUNCTIONS
# =====================================================

def load_history():
    cursor = db.execute(
        "SELECT role, content, tokens FROM chats WHERE session_id=? ORDER BY id",
        (st.session_state.session_id,)
    )
    rows = cursor.fetchall()
    st.session_state.messages = [
        {"role": r[0], "content": r[1], "tokens": r[2]} for r in rows
    ]
    st.session_state.total_tokens = sum(r[2] for r in rows if r[2])

if not st.session_state.messages:
    load_history()


def save_message(role, content, tokens):
    db.execute(
        "INSERT INTO chats (session_id, role, content, tokens, timestamp) VALUES (?, ?, ?, ?, ?)",
        (
            st.session_state.session_id,
            role,
            content,
            tokens,
            datetime.now().isoformat()
        )
    )
    db.commit()


# =====================================================
# LLM INIT
# =====================================================

llm = None
token_handler = TokenCounter()

if LANGCHAIN_AVAILABLE and OPENROUTER_API_KEY:
    try:
        llm = ChatOpenAI(
            model=st.session_state.model_name,
            temperature=st.session_state.temperature,
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
            callbacks=[token_handler]
        )
    except Exception as e:
        st.error(f"LLM init error: {e}")


# =====================================================
# LOGIN
# =====================================================

if not st.session_state.logged_in:
    st.title("AI Pro Enterprise+")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if pwd == APP_PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
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
    st.metric("Messages", len(st.session_state.messages))
    st.metric("Total Tokens", st.session_state.total_tokens)

    if st.button("Export Chat"):
        export_data = json.dumps(st.session_state.messages, indent=2)
        st.download_button("Download JSON", export_data, "chat_export.json")

    if st.button("Clear Chat"):
        db.execute("DELETE FROM chats WHERE session_id=?",
                   (st.session_state.session_id,))
        db.commit()
        st.session_state.messages = []
        st.session_state.total_tokens = 0
        st.rerun()

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()


# =====================================================
# MAIN
# =====================================================

st.title("🚀 AI Pro Enterprise+")


# =====================================================
# CHAT
# =====================================================

if page == "Chat":

    if not llm:
        st.warning("Set OPENROUTER_API_KEY in secrets.")
        st.stop()

    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if st.button("Delete", key=f"del_{i}"):
                db.execute("DELETE FROM chats WHERE session_id=? AND content=?",
                           (st.session_state.session_id, msg["content"]))
                db.commit()
                st.session_state.messages.pop(i)
                st.rerun()

    if prompt := st.chat_input("Ask something..."):

        st.session_state.messages.append({"role": "user", "content": prompt, "tokens": 0})
        save_message("user", prompt, 0)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""

            messages = [SystemMessage(content=st.session_state.system_prompt)]

            for m in st.session_state.messages[-st.session_state.context_window:]:
                if m["role"] == "user":
                    messages.append(HumanMessage(content=m["content"]))
                else:
                    messages.append(AIMessage(content=m["content"]))

            try:
                for chunk in llm.stream(messages):
                    full_response += chunk.content or ""
                    placeholder.markdown(full_response + "▌")

                placeholder.markdown(full_response)

                tokens_used = token_handler.total_tokens
                st.session_state.total_tokens += tokens_used

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response,
                    "tokens": tokens_used
                })

                save_message("assistant", full_response, tokens_used)

            except Exception as e:
                placeholder.markdown(f"Error: {e}")


# =====================================================
# ANALYTICS
# =====================================================

elif page == "Analytics":

    st.header("Usage Analytics")

    cursor = db.execute("""
        SELECT DATE(timestamp), COUNT(*)
        FROM chats
        GROUP BY DATE(timestamp)
        ORDER BY DATE(timestamp)
    """)
    rows = cursor.fetchall()

    if rows and ANALYTICS_AVAILABLE:
        df = pd.DataFrame(rows, columns=["Date", "Messages"])
        fig = px.line(df, x="Date", y="Messages", title="Messages per Day")
        st.plotly_chart(fig, use_container_width=True)

        role_df = pd.read_sql_query(
            "SELECT role, COUNT(*) as count FROM chats GROUP BY role",
            db
        )
        fig2 = px.pie(role_df, names="role", values="count", title="Role Distribution")
        st.plotly_chart(fig2, use_container_width=True)

    else:
        st.info("No analytics data yet.")


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

    st.session_state.context_window = st.slider(
        "Context Window (messages)",
        3,
        20,
        st.session_state.context_window
    )

    st.session_state.system_prompt = st.text_area(
        "System Prompt",
        st.session_state.system_prompt,
        height=150
    )

    st.info("Changes apply immediately.")
