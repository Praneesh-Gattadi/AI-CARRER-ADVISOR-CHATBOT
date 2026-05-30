# ================== app.py ==================
import os
import streamlit as st
import uuid
import re
from dotenv import load_dotenv
from loguru import logger

from gemini_service import GeminiService
from prompt_manager import PromptManager
from db_manager import DBManager
from auth_validators import validate_password_strength, validate_email_format
from email_service import send_verification_email

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Carrer Coach", page_icon="🚀", layout="wide")

# ── Logger ────────────────────────────────────────────────────────────────────
@st.cache_resource
def configure_logger():
    logger.add("app.log", rotation="10 MB", retention="7 days", level="INFO")
    return True

configure_logger()

# ── Database Initialization ───────────────────────────────────────────────────
DBManager.init_db()

# ── Authentication View ───────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""

# Streamlit OTP verification state machine
if st.session_state.get("pending_verification"):
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("Carrer Coach")
        st.markdown("### Verify Your Email")
        st.markdown(
            f"We sent a 6-digit verification code to **{st.session_state['pending_email']}**.<br>"
            "Please enter it below to complete your registration.",
            unsafe_allow_html=True
        )
        
        otp_code = st.text_input("Verification Code", max_chars=6, key="otp_code_input", placeholder="••••••").strip()
        
        col_verify, col_resend, col_cancel = st.columns([1.5, 1.5, 1])
        
        with col_verify:
            if st.button("Verify & Sign In", use_container_width=True, key="verify_otp_btn"):
                if not otp_code or len(otp_code) != 6:
                    st.error("⚠️ Please enter a valid 6-digit verification code.")
                else:
                    pending = DBManager.get_pending_user(st.session_state["pending_username"])
                    if not pending:
                        st.error("❌ Registration session not found. Please sign up again.")
                        st.session_state["pending_verification"] = False
                        st.rerun()
                    elif pending["otp"] != otp_code:
                        st.error("❌ Invalid verification code. Please try again.")
                    else:
                        success = DBManager.register_user(
                            username=pending["username"],
                            email=pending["email"],
                            password=pending["password_hash"],
                            password_already_hashed=True
                        )
                        if success:
                            DBManager.delete_pending_user(pending["username"])
                            st.session_state["logged_in"] = True
                            st.session_state["username"] = pending["username"]
                            st.session_state["pending_verification"] = False
                            st.success("🎉 Account verified and created successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to complete registration.")
                            
        with col_resend:
            if st.button("Resend Code", use_container_width=True, key="resend_otp_btn"):
                pending = DBManager.get_pending_user(st.session_state["pending_username"])
                if not pending:
                    st.error("❌ Registration session not found. Please sign up again.")
                    st.session_state["pending_verification"] = False
                    st.rerun()
                else:
                    import random
                    new_otp = f"{random.randint(100000, 999999)}"
                    with DBManager.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "UPDATE pending_users SET otp = ?, created_at = CURRENT_TIMESTAMP WHERE username = ?",
                            (new_otp, st.session_state["pending_username"])
                        )
                        conn.commit()
                    success, mail_msg = send_verification_email(pending["email"], pending["username"], new_otp)
                    st.info(f"📩 Code resent to {pending['email']}. Check inbox or terminal logs.")
                    
        with col_cancel:
            if st.button("Cancel Flow", use_container_width=True, key="cancel_otp_btn"):
                DBManager.delete_pending_user(st.session_state["pending_username"])
                st.session_state["pending_verification"] = False
                st.rerun()
    st.stop()

if not st.session_state["logged_in"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("Carrer Coach")
        st.caption("Enterprise SaaS Platform · Cryptographic Security · Model: Gemini 1.5")
        st.markdown("---")
        
        tab_login, tab_register = st.tabs(["🔑 Sign In", "📝 Create Account"])
        
        with tab_login:
            st.markdown("### Welcome Back!")
            li_user = st.text_input("Username", key="li_user_input", placeholder="e.g. alex_stone").strip().lower()
            li_pass = st.text_input("Password", type="password", key="li_pass_input", placeholder="••••••••")
            
            if st.button("Sign In", use_container_width=True, key="login_btn"):
                if not li_user or not li_pass:
                    st.error("⚠️ Username and Password are required.")
                elif DBManager.verify_user(li_user, li_pass):
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = li_user
                    st.success("✅ Signed in successfully! Loading dashboard...")
                    st.rerun()
                else:
                    st.error("❌ Incorrect username or password. Please try again.")
                    
        with tab_register:
            st.markdown("### Join Carrer Coach!")
            reg_user = st.text_input("Choose Username", key="reg_user_input", placeholder="e.g. alex_stone").strip().lower()
            reg_email = st.text_input("Email Address", key="reg_email_input", placeholder="e.g. alex@example.com").strip()
            reg_pass = st.text_input("Choose Password", type="password", key="reg_pass_input", placeholder="••••••••")
            reg_pass_confirm = st.text_input("Confirm Password", type="password", key="reg_pass_confirm_input", placeholder="••••••••")
            
            st.markdown(
                "<p style='font-size: 11px; color: #9ca3af; line-height: 1.4; margin: -5px 0 15px 0;'>"
                "💡 <strong>Password requirements:</strong> Minimum 8 characters, "
                "at least 1 uppercase, 1 lowercase, 1 digit, and 1 special character.</p>",
                unsafe_allow_html=True
            )
            
            if st.button("Send Verification OTP", use_container_width=True, key="reg_btn"):
                if not reg_user or not reg_email or not reg_pass:
                    st.error("⚠️ Username, Email, and Password are required.")
                elif not validate_email_format(reg_email):
                    st.error("❌ Invalid email format. E.g. user@example.com")
                elif reg_pass != reg_pass_confirm:
                    st.error("⚠️ Passwords do not match.")
                else:
                    # Validate password strength
                    is_strong, error_msg = validate_password_strength(reg_pass)
                    if not is_strong:
                        st.error(f"❌ {error_msg}")
                    else:
                        # Check if username is already registered and verified
                        with DBManager.get_connection() as conn:
                            cursor = conn.cursor()
                            cursor.execute("SELECT 1 FROM users WHERE username = ?", (reg_user,))
                            if cursor.fetchone():
                                st.error("❌ Username already exists. Please choose a different one.")
                            else:
                                # Generate OTP
                                import random
                                otp = f"{random.randint(100000, 999999)}"
                                
                                # Store pending details
                                DBManager.save_pending_user(reg_user, reg_email, reg_pass, otp)
                                
                                # Send verification email (with fallback logic)
                                success, mail_msg = send_verification_email(reg_email, reg_user, otp)
                                
                                # Transition to pending verification screen
                                st.session_state["pending_verification"] = True
                                st.session_state["pending_username"] = reg_user
                                st.session_state["pending_email"] = reg_email
                                st.success(f"📩 Verification code sent to {reg_email}. Please check inbox or console logs!")
                                st.rerun()
    st.stop()

# ── Loaded User Info ──────────────────────────────────────────────────────────
username = st.session_state["username"]

# ── Goal checklist parser helper ──────────────────────────────────────────────
def parse_checklist_goals(response_text: str) -> list:
    """Parses bullet point actionable items out of the assistant response."""
    goals = []
    if not response_text:
        return goals
    # Clean lines split
    lines = response_text.split("\n")
    for line in lines:
        line = line.strip()
        # Find bullet point items
        match = re.match(r"^[-*+•] (.*)$", line)
        if match:
            goal = match.group(1).strip()
            # Clean off formatting markdown tags
            goal = re.sub(r"\*\*|__", "", goal)
            # Limit length and check if it's actual instruction steps
            if len(goal) > 5 and len(goal) < 80 and not goal.startswith("[") and not goal.startswith("```"):
                goals.append(goal)
    return goals[:6]  # Max 6 actionable goal items

def extract_text_from_file(file_obj) -> str:
    """Extracts text from uploaded PDF, TXT, or DOCX resume files."""
    if not file_obj:
        return ""
    try:
        name = file_obj.name.lower()
        if name.endswith(".pdf"):
            from pypdf import PdfReader
            reader = PdfReader(file_obj)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text.strip()
        elif name.endswith(".docx"):
            import docx
            doc = docx.Document(file_obj)
            text = ""
            for para in doc.paragraphs:
                if para.text:
                    text += para.text + "\n"
            return text.strip()
        elif name.endswith(".txt"):
            return file_obj.read().decode("utf-8", errors="ignore").strip()
    except Exception as e:
        logger.error(f"Failed to parse resume file {file_obj.name}: {str(e)}")
    return ""

# ── Load .env ─────────────────────────────────────────────────────────────────
ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=ENV_PATH)

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

logger.info(f"API Key loaded for {username}: {'YES (' + GOOGLE_API_KEY[:8] + '...)' if GOOGLE_API_KEY else 'NOT FOUND'}")

if not GOOGLE_API_KEY:
    st.error("❌ **GEMINI_API_KEY** or **GOOGLE_API_KEY** not found. Make sure your file is named exactly `.env` (not `_env`) and contains:\n\n`GOOGLE_API_KEY=your_key_here`")
    st.stop()

# ── Initialize Gemini Service ─────────────────────────────────────────────────
@st.cache_resource
def get_gemini_service(key: str):
    return GeminiService(api_key=key)

gemini = get_gemini_service(GOOGLE_API_KEY)

# ── Session State Management ──────────────────────────────────────────────────
if "active_session_id" not in st.session_state:
    sessions = DBManager.get_all_sessions(username)
    if sessions:
        st.session_state["active_session_id"] = sessions[0]["id"]
    else:
        new_id = str(uuid.uuid4())
        st.session_state["active_session_id"] = new_id
        DBManager.create_session(new_id, username, "New Career Session")

active_session_id = st.session_state["active_session_id"]

# ── Sidebar Widgets ───────────────────────────────────────────────────────────
with st.sidebar:
    st.title("Carrer Coach")
    st.markdown("---")

    # 1. New Session Trigger
    if st.button("➕ Start New Career Chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state["active_session_id"] = new_id
        DBManager.create_session(new_id, username, "New Career Session")
        logger.info(f"➕ Private new chat session created for {username} | UUID={new_id}")
        st.rerun()

    # 2. Saved Career Sessions list
    sessions = DBManager.get_all_sessions(username)
    session_ids = [s["id"] for s in sessions]
    session_titles = {s["id"]: s["title"] for s in sessions}

    if active_session_id not in session_ids:
        DBManager.create_session(active_session_id, username, "New Career Session")
        sessions = DBManager.get_all_sessions(username)
        session_ids = [s["id"] for s in sessions]
        session_titles = {s["id"]: s["title"] for s in sessions}

    selected_session_id = st.selectbox(
        "📜 Saved Career Sessions",
        options=session_ids,
        format_func=lambda x: session_titles.get(x, "New Career Session"),
        index=session_ids.index(active_session_id) if active_session_id in session_ids else 0
    )

    if selected_session_id != active_session_id:
        st.session_state["active_session_id"] = selected_session_id
        logger.info(f"🔄 Switched active session to UUID={selected_session_id}")
        st.rerun()

    # Provide clear delete option for selected session
    if st.button("🗑️ Delete Selected Chat", use_container_width=True):
        DBManager.delete_session(active_session_id)
        remaining = DBManager.get_all_sessions(username)
        if remaining:
            st.session_state["active_session_id"] = remaining[0]["id"]
        else:
            new_id = str(uuid.uuid4())
            st.session_state["active_session_id"] = new_id
            DBManager.create_session(new_id, username, "New Career Session")
        st.rerun()

    st.markdown("---")

    # 3. Profile Customization Accordion
    with st.expander("👤 1. Customize Your Profile", expanded=True):
        education = st.selectbox(
            "Education Level",
            ["Not specified", "High School / Student", "Fresh Graduate / College Student", "Mid-career Switcher", "Senior Professional"],
            index=0
        )
        experience = st.selectbox(
            "Experience Level",
            ["Not specified", "0-2 Years (Entry)", "3-5 Years (Mid)", "5+ Years (Senior)"],
            index=0
        )
        target_goal = st.text_input(
            "Target Goal / Role",
            placeholder="e.g. Data Scientist, AI Engineer"
        )
        
        # Build profile dict for Gemini context
        profile_dict = {
            "education": education if education != "Not specified" else None,
            "experience": experience if experience != "Not specified" else None,
            "target_goal": target_goal if target_goal.strip() else None
        }

    # 4. Resume Uploader Accordion
    with st.expander("📄 2. Upload Your Resume/CV", expanded=False):
        uploaded_file = st.file_uploader(
            "Upload resume to personalize advice",
            type=["pdf", "txt", "docx"],
            help="Extracts text to customize suggestions based on your projects, background, and skills."
        )
        
        resume_text = ""
        if uploaded_file:
            resume_text = extract_text_from_file(uploaded_file)
            if resume_text:
                st.success("✅ Resume parsed successfully!")
            else:
                st.warning("⚠️ Could not extract text from the file.")

    # 5. Standalone Log Out button
    if st.button("🚪 Log Out", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state.pop("active_session_id", None)
        logger.info("🚪 User logged out successfully")
        st.rerun()

    st.markdown("---")
    st.caption("Powered by **Google Gemini 1.5 & Search Grounding**")

# ── Main Header Container ─────────────────────────────────────────────────────
col_title, col_export = st.columns([3, 1])
with col_title:
    st.title("Carrer Coach")
with col_export:
    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
    history = DBManager.get_messages(active_session_id)
    if history:
        chat_md = "# Carrer Coach - Custom Advisor Roadmap & Report\n\n"
        chat_md += "## 👤 User Profile Context\n"
        chat_md += f"- **Education:** {education}\n"
        chat_md += f"- **Experience:** {experience}\n"
        chat_md += f"- **Target Goal:** {target_goal if target_goal else 'Not specified'}\n"
        if uploaded_file:
            chat_md += f"- **Resume:** {uploaded_file.name} (Uploaded & Parsed)\n"
        chat_md += "\n---\n\n## 💬 Conversation Roadmap & Advice\n\n"
        
        for msg in history:
            role_label = "👤 User Query" if msg["role"].lower() == "user" else "🤖 Advisor Recommendation"
            chat_md += f"### {role_label}\n{msg['content'].strip()}\n\n"
            
        st.download_button(
            label="📥 Export Roadmap",
            data=chat_md,
            file_name=f"career_roadmap_{username}.md",
            mime="text/markdown",
            use_container_width=True
        )
    else:
        st.button("📥 Export Roadmap", disabled=True, use_container_width=True)

st.markdown("---")

# Chat Display
if not history:
    st.info("👋 Welcome! Ask a career strategy query or select a historical session in the sidebar to begin!")

for msg in history:
    with st.chat_message(msg["role"].lower()):
        st.markdown(msg["content"].strip())



# Chat Input
if "pill_query" in st.session_state and st.session_state["pill_query"]:
    user_input = st.session_state["pill_query"]
    del st.session_state["pill_query"]
else:
    user_input = st.chat_input("Ask your career question here...", key="strategy_chat_input")

if user_input:
    logger.info(f"👤 User strategy query received | length={len(user_input)}")

    with st.chat_message("user"):
        st.markdown(user_input)

    DBManager.add_message(active_session_id, "user", user_input)

    with st.chat_message("assistant"):
        formatted_messages = []
        for msg in history:
            role = "user" if msg["role"].lower() == "user" else "model"
            formatted_messages.append({"role": role, "content": msg["content"]})
        formatted_messages.append({"role": "user", "content": user_input})
        
        system_instruction = PromptManager.get_system_prompt(
            profile=profile_dict,
            resume_text=resume_text if resume_text else None
        )
        
        response = st.write_stream(
            gemini.generate_response_stream(
                messages=formatted_messages,
                system_instruction=system_instruction
            )
        )

    DBManager.add_message(active_session_id, "assistant", response)
    logger.info("✅ Response delivered to user")
    st.rerun()
