# 🚀 AI Career Advisor Chatbot

A **Production-Ready Domain-Specific Chatbot** built with **Google Gemini 2.0 API** and **Streamlit**.

---

## 📌 Project Overview
This chatbot provides intelligent, structured career guidance to students and professionals. It supports multi-turn conversations, advanced prompt engineering, and follows a clean modular architecture to ensure scalability and production-grade performance.

**Domain:** Career Guidance  
**Model:** Gemini 2.0 Flash (Google)  
**UI:** Streamlit  
**Deployment:** AWS EC2 (Ubuntu)  

---

## 🏗️ System Architecture
User
└─► Streamlit UI (app.py)
└─► ChatMemory (chat_memory.py)      ← Session-based memory
└─► PromptManager (prompt_manager.py) ← Domain guardrails
└─► GeminiService (gemini_service.py) ← API & Fallback layer
└─► Google Gemini API
└─► Response → UI Rendering

### Module Responsibilities
* **`app.py`**: Manages the UI layer, including layout, user input handling, and real-time response rendering.
* **`gemini_service.py`**: Handles all communication with the Gemini API, including a robust fallback loop for high availability and structured logging.
* **`prompt_manager.py`**: Manages system prompts, persona constraints, and ensures the bot only answers career-related queries.
* **`chat_memory.py`**: Implements a memory layer to maintain context across multi-turn conversations.

---

## ⚙️ Local Setup

### 1. Clone the repository
```bash
git clone [https://github.com/Praneesh-Gattadi/ai-career-advisor-chatbot.git](https://github.com/Praneesh-Gattadi/ai-career-advisor-chatbot.git)
cd ai-career-advisor-chatbot
2. Create a virtual environment
Bash
python -m venv venv
venv\Scripts\activate  # Windows
3. Install dependencies
Bash
pip install -r requirements.txt
4. Configure environment variables
Create a .env file and add your Google API key:

Bash
GOOGLE_API_KEY=your_gemini_api_key_here
5. Run the app
Bash
streamlit run app.py
☁️ AWS EC2 Deployment
Step 1: Configure Security Group
The following Inbound Rules were added to the AWS EC2 instance to allow public access:

SSH (Port 22): For remote access via terminal.

Custom TCP (Port 8501): To expose the Streamlit web interface.

Step 2: Running in Background
To satisfy the "Background process execution" requirement, the app is launched using nohup:

Bash
nohup python -m streamlit run app.py > streamlit.log 2>&1 &
This ensures the chatbot remains online even after the SSH session is closed.

🔐 Security & Best Practices
API Key Protection: API keys are stored in a .env file and are never hardcoded in the source files.

Git Security: A .gitignore file is implemented to prevent sensitive files like .env and .pem keys from being uploaded to GitHub.

✅ Deliverables Summary
[x] Functional Chatbot: Modular and production-grade.

[x] Domain Specific: Limited to career-related guidance.

[x] Cloud Deployed: Hosted on AWS EC2.

[x] Persistent: Running as a background process.