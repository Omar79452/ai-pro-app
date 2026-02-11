import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import json
import os
from io import BytesIO
import requests
from PIL import Image

# Optional analytics
try:
    import pandas as pd
    import plotly.express as px
    ANALYTICS_AVAILABLE = True
except:
    ANALYTICS_AVAILABLE = False

# LangChain
try:
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    from langchain_community.vectorstores import FAISS
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.document_loaders import PyPDFLoader
    LANGCHAIN_AVAILABLE = True
except:
    LANGCHAIN_AVAILABLE = False


# =====================================================
# CONFIG
# =====================================================

st.set_page_config(page_title="AI Pro Enterprise++", layout="wide")

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
# SESSION INIT
# =====================================================

def init_session():
    defaults = {
        "logged_in": False,
        "session_id": hashlib.md5(str(datetime.now()).encode()).hexdigest()[:10],
        "messages": [],
        "vectorstore": None,
        "rag_enabled": False,
        "model_name": "openai/gpt-4o-mini",
        "temperature": 0.7,
        "system_prompt": "You are a professional AI assistant."
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# =====================================================
# LLM INIT
# =====================================================

llm = None
embeddings = None

if LANGCHAIN_AVAILABLE and OPENROUTER_API_KEY:
    try:
        llm = ChatOpenAI(
            model=st.session_state.model_name,
            temperature=st.session_state.temperature,
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )

        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )

    except Exception as e:
        st.error(f"LLM init error: {e}")


# =====================================================
# LOGIN
# =====================================================

if not st.session_state.logged_in:
    st.title("AI Pro Enterprise++")
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
    st.header("Navigation")

    page = st.radio("Go to", [
        "Chat",
        "RAG",
        "Image Generation",
        "Settings"
    ])

    st.divider()

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()


# =====================================================
# CHAT
# =====================================================

if page == "Chat":

    st.title("💬 AI Chat")

    if not llm:
        st.warning("Add OPENROUTER_API_KEY to secrets.")
        st.stop()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask something..."):

        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full = ""

            messages = [SystemMessage(content=st.session_state.system_prompt)]

            # RAG context if enabled
            if st.session_state.rag_enabled and st.session_state.vectorstore:
                docs = st.session_state.vectorstore.similarity_search(prompt, k=3)
                context = "\n\n".join([d.page_content for d in docs])
                messages.append(SystemMessage(content=f"Context:\n{context}"))

            for m in st.session_state.messages[-6:]:
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


# =====================================================
# RAG
# =====================================================

elif page == "RAG":

    st.title("📄 Document RAG")

    if not embeddings:
        st.warning("Embeddings not available.")
        st.stop()

    uploaded_file = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"])

    if uploaded_file:

        with st.spinner("Processing document..."):

            if uploaded_file.type == "application/pdf":
                with open("temp.pdf", "wb") as f:
                    f.write(uploaded_file.read())
                loader = PyPDFLoader("temp.pdf")
                documents = loader.load()
            else:
                text = uploaded_file.read().decode("utf-8")
                documents = [{"page_content": text}]

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )

            docs = splitter.split_documents(documents)

            vectorstore = FAISS.from_documents(docs, embeddings)
            st.session_state.vectorstore = vectorstore
            st.session_state.rag_enabled = True

            st.success("RAG enabled. You can now ask questions in Chat.")


# =====================================================
# IMAGE GENERATION
# =====================================================

elif page == "Image Generation":

    st.title("🖼️ AI Image Generation")

    prompt = st.text_area("Describe your image", height=100)

    size = st.selectbox("Size", ["512x512", "1024x1024"])

    if st.button("Generate Image") and prompt:

        with st.spinner("Generating image..."):

            try:
                clean_prompt = prompt.replace(" ", "%20")
                url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width={size.split('x')[0]}&height={size.split('x')[1]}"
                img = Image.open(BytesIO(requests.get(url, timeout=30).content))
                st.image(img, caption=prompt, use_column_width=True)
            except Exception as e:
                st.error(f"Image generation failed: {e}")


# =====================================================
# SETTINGS
# =====================================================

elif page == "Settings":

    st.title("⚙️ Settings")

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

    st.session_state.system_prompt = st.text_area(
        "System Prompt",
        st.session_state.system_prompt,
        height=150
    )

    st.info("Changes apply immediately.")
