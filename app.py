# ================== app.py ==================
import os
import streamlit as st
from dotenv import load_dotenv
from loguru import logger

from gemini_service import GeminiService
from prompt_manager import PromptManager
from chat_memory import ChatMemory

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="AI Career Advisor", page_icon="🚀", layout="wide")

# ── Logger ────────────────────────────────────────────────────────────────────
logger.add("app.log", rotation="500 KB", retention="7 days", level="INFO")

# ── Load .env ─────────────────────────────────────────────────────────────────
ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=ENV_PATH)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Debug: print to terminal so you can verify the key is loading
print(f"\n🔑 GOOGLE_API_KEY loaded: {'✅ YES (' + GOOGLE_API_KEY[:8] + '...)' if GOOGLE_API_KEY else '❌ NOT FOUND'}\n")

if not GOOGLE_API_KEY:
    st.error("❌ **GOOGLE_API_KEY** not found. Make sure your file is named exactly `.env` (not `_env`) and contains:\n\n`GOOGLE_API_KEY=your_key_here`")
    st.stop()

# ── Initialize Modules ────────────────────────────────────────────────────────
ChatMemory.init()

@st.cache_resource
def get_gemini_service(key: str):
    return GeminiService(api_key=key)

gemini = get_gemini_service(GOOGLE_API_KEY)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/rocket.png", width=64)
    st.title("AI Career Advisor")
    st.markdown("---")
    st.markdown(
        "💡 **Ask me about:**\n"
        "- Career paths & transitions\n"
        "- Skills & certifications\n"
        "- Job market trends\n"
        "- Resume & interview tips\n"
        "- Learning roadmaps"
    )
    st.markdown("---")
    count = ChatMemory.message_count()
    st.caption(f"💬 Messages in session: **{count}**")
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        ChatMemory.clear()
        logger.info("🗑️ Chat history cleared by user")
        st.rerun()
    st.markdown("---")
    st.caption("Powered by **Google Gemini**")

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🚀 AI Career Advisor Chatbot")
st.caption("Production-Ready GenAI Assistant · Domain: Career Guidance · Model: Gemini 2.0 Flash")
st.markdown("---")

# ── Chat Display ──────────────────────────────────────────────────────────────
history = ChatMemory.get_history()
if not history:
    st.info("👋 Hello! I'm your AI Career Advisor. Ask me anything about your career goals, skills to learn, or next steps!")

for msg in history:
    role, content = msg.split(":", 1)
    with st.chat_message(role.strip().lower()):
        st.markdown(content.strip())

# ── Chat Input ────────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask your career question here...")

if user_input:
    logger.info(f"👤 User input received | length={len(user_input)}")

    with st.chat_message("user"):
        st.markdown(user_input)

    ChatMemory.add_message("User", user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            prompt = PromptManager.build_prompt(
                user_query=user_input,
                chat_history=ChatMemory.get_history()
            )
            response = gemini.generate_response(prompt=prompt)
        st.markdown(response)

    ChatMemory.add_message("Assistant", response)
    logger.info("✅ Response delivered to user")
    st.rerun()
