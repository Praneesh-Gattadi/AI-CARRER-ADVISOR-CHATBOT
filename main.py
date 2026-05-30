# ================== main.py ==================
import os
import uuid
import json
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from loguru import logger
from dotenv import load_dotenv

from db_manager import DBManager
from gemini_service import GeminiService
from prompt_manager import PromptManager
from auth_validators import validate_password_strength, validate_email_format
from email_service import send_verification_email

# ── Load Env & Key ────────────────────────────────────────────────────────────
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    logger.error("❌ Google Gemini API Key not found in environment!")
    # We will raise exceptions in routes if key is missing

# ── Service Initializer ───────────────────────────────────────────────────────
gemini = GeminiService(api_key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None
DBManager.init_db()

# ── FastAPI App Setup ─────────────────────────────────────────────────────────
app = FastAPI(title="Carrer Coach API", version="1.0.0")

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Disable browser caching for static files during development
@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.endswith((".html", ".js", ".css")) or request.url.path == "/":
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# ── Request / Response Models ─────────────────────────────────────────────────
class UserAuth(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class OTPVerifyRequest(BaseModel):
    username: str
    otp: str

class OTPResendRequest(BaseModel):
    username: str

class ChatSendRequest(BaseModel):
    session_id: str
    username: str
    message: str
    education: Optional[str] = "Not specified"
    experience: Optional[str] = "Not specified"
    target_goal: Optional[str] = ""
    resume_text: Optional[str] = ""

# ── Helper: Parse checklist goals ─────────────────────────────────────────────
def parse_goals(text: str) -> List[str]:
    import re
    goals = []
    if not text:
        return goals
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        match = re.match(r"^[-*+•] (.*)$", line)
        if match:
            g = match.group(1).strip()
            g = re.sub(r"\*\*|__", "", g)
            if len(g) > 5 and len(g) < 80 and not g.startswith("[") and not g.startswith("```"):
                goals.append(g)
    return goals[:6]

# ── REST API ROUTES ───────────────────────────────────────────────────────────

@app.post("/api/auth/register")
def register(user: UserAuth):
    username = user.username.strip().lower()
    email = user.email.strip() if user.email else ""
    
    if not username or not user.password or not email:
        raise HTTPException(status_code=400, detail="Username, Email, and Password are required.")
    
    # 1. Validate email structure
    if not validate_email_format(email):
        raise HTTPException(status_code=400, detail="Invalid email format. E.g. user@example.com")
        
    # 2. Validate password strength
    is_strong, error_msg = validate_password_strength(user.password)
    if not is_strong:
        raise HTTPException(status_code=400, detail=error_msg)
        
    # 3. Check if username is already registered
    with DBManager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username already exists.")
            
    # Directly register user to users table (bypass OTP/verification email)
    success = DBManager.register_user(
        username=username,
        email=email,
        password=user.password,
        password_already_hashed=False
    )
    
    if success:
        return {
            "status": "registered",
            "message": "Registration successful",
            "username": username,
            "email": email
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to complete user registration. Please retry.")

@app.post("/api/auth/verify-otp")
def verify_otp(req: OTPVerifyRequest):
    username = req.username.strip().lower()
    otp = req.otp.strip()
    
    pending = DBManager.get_pending_user(username)
    if not pending:
        raise HTTPException(status_code=404, detail="No pending registration session found for this user.")
        
    if pending["otp"] != otp:
        raise HTTPException(status_code=400, detail="Invalid verification code. Please try again.")
        
    # Account verification succeeded! Save verified user to users database
    success = DBManager.register_user(
        username=pending["username"],
        email=pending["email"],
        password=pending["password_hash"],
        password_already_hashed=True
    )
    
    if success:
        DBManager.delete_pending_user(username)
        return {"message": "Registration successful", "username": username}
    else:
        raise HTTPException(status_code=500, detail="Failed to complete user registration. Please retry.")

@app.post("/api/auth/resend-otp")
def resend_otp(req: OTPResendRequest):
    username = req.username.strip().lower()
    
    pending = DBManager.get_pending_user(username)
    if not pending:
        raise HTTPException(status_code=404, detail="No pending registration session found for this user.")
        
    import random
    new_otp = f"{random.randint(100000, 999999)}"
    
    # Update pending signup record with new verification OTP
    with DBManager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE pending_users SET otp = ?, created_at = CURRENT_TIMESTAMP WHERE username = ?",
            (new_otp, username)
        )
        conn.commit()
        
    success, mail_msg = send_verification_email(pending["email"], username, new_otp)
    
    return {
        "status": "verification_pending",
        "message": f"New verification code sent to {pending['email']}. " + mail_msg,
        "username": username,
        "email": pending["email"]
    }

@app.post("/api/auth/login")
def login(user: UserAuth):
    username = user.username.strip().lower()
    if DBManager.verify_user(username, user.password):
        return {"message": "Login successful", "username": username}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password.")

@app.get("/api/sessions")
def get_sessions(username: str = Query(...)):
    sessions = DBManager.get_all_sessions(username)
    return {"sessions": sessions}

@app.post("/api/sessions/create")
def create_session(payload: dict):
    username = payload.get("username", "").strip().lower()
    if not username:
        raise HTTPException(status_code=400, detail="Username is required.")
    new_id = str(uuid.uuid4())
    DBManager.create_session(new_id, username, "New Career Session")
    return {"session_id": new_id, "title": "New Career Session"}

@app.delete("/api/sessions/delete")
def delete_session(session_id: str = Query(...)):
    DBManager.delete_session(session_id)
    return {"message": "Session deleted successfully"}

@app.get("/api/chat/messages")
def get_chat_messages(session_id: str = Query(...)):
    messages = DBManager.get_messages(session_id)
    return {"messages": messages}

@app.post("/api/chat/send")
def send_chat_message(req: ChatSendRequest):
    if not gemini:
        raise HTTPException(status_code=500, detail="Gemini Service is offline (API Key missing).")
    
    # Save user message
    DBManager.add_message(req.session_id, "user", req.message)
    
    # Fetch conversation history from database
    history = DBManager.get_messages(req.session_id)
    
    # Format messages for Gemini client
    formatted = []
    for msg in history:
        role = "user" if msg["role"].lower() == "user" else "model"
        formatted.append({"role": role, "content": msg["content"]})
    
    profile = {
        "education": req.education if req.education != "Not specified" else None,
        "experience": req.experience if req.experience != "Not specified" else None,
        "target_goal": req.target_goal if req.target_goal.strip() else None
    }
    
    system_instruction = PromptManager.get_system_prompt(
        profile=profile,
        resume_text=req.resume_text if req.resume_text else None
    )
    
    try:
        response_text = gemini.generate_response(
            messages=formatted,
            system_instruction=system_instruction
        )
        # Save assistant message
        DBManager.add_message(req.session_id, "assistant", response_text)
        
        # Calculate parsed checklist items
        goals = parse_goals(response_text)
        
        return {"response": response_text, "goals": goals}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini error: {str(e)}")

class ProfileSaveRequest(BaseModel):
    username: str
    education: Optional[str] = "Not specified"
    experience: Optional[str] = "Not specified"
    target_goal: Optional[str] = ""

@app.get("/api/profile")
def get_profile(username: str = Query(...)):
    profile = DBManager.get_user_profile(username)
    if profile is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return profile

@app.post("/api/profile/save")
def save_profile(req: ProfileSaveRequest):
    success = DBManager.save_user_profile(
        username=req.username,
        education=req.education,
        experience=req.experience,
        target_goal=req.target_goal
    )
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save profile.")
    return {"message": "Profile saved successfully"}

@app.post("/api/resume/upload")
async def upload_resume(username: Optional[str] = Query(None), file: UploadFile = File(...)):
    name = file.filename.lower()
    if not (name.endswith(".pdf") or name.endswith(".txt") or name.endswith(".docx")):
        raise HTTPException(status_code=400, detail="Only PDF, TXT, or DOCX files are allowed.")
    
    try:
        content = await file.read()
        extracted_text = ""
        
        if name.endswith(".pdf"):
            import io
            from pypdf import PdfReader
            pdf_file = io.BytesIO(content)
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    extracted_text += t + "\n"
        elif name.endswith(".docx"):
            import io
            import docx
            docx_file = io.BytesIO(content)
            doc = docx.Document(docx_file)
            for para in doc.paragraphs:
                if para.text:
                    extracted_text += para.text + "\n"
        else:
            extracted_text = content.decode("utf-8", errors="ignore")
            
        text_clean = extracted_text.strip()
        
        if username:
            existing = DBManager.get_user_profile(username)
            edu = "Not specified"
            exp = "Not specified"
            goal = ""
            if existing:
                edu = existing.get("education") or "Not specified"
                exp = existing.get("experience") or "Not specified"
                goal = existing.get("target_goal") or ""
            DBManager.save_user_profile(
                username=username,
                education=edu,
                experience=exp,
                target_goal=goal,
                resume_text=text_clean,
                resume_filename=file.filename
            )
            
        return {"text": text_clean}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse file: {str(e)}")

# ── Serve Static Frontend Assets ──────────────────────────────────────────────
# We will create the `frontend/` directory and mount it statically as the root root.
# Make sure frontend is hosted on the "/" route
os.makedirs("frontend", exist_ok=True)
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    # Bind to port 8000
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
