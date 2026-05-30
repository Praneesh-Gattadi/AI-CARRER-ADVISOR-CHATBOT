# Carrer Coach - Premium AI Career Strategy Hub

A production-ready, enterprise-grade Generative AI Career Advisor chatbot platform. Built on a modular architecture featuring a high-society luxury design system, stateful multi-tenant SQLite session isolation, and real-time Google Gemini grounding.

---

## 📌 Project Overview
**Carrer Coach** (strictly spelled *Carrer Coach*) provides elite, structured career strategy guidance to students, mid-career switchers, and executives. The platform has been refined with a high-end bespoke aesthetic paired with a high-speed, OTP-free user authentication system.

* **Domain:** AI Career Strategy & Bespoke Executive Coaching
* **Model:** Google Gemini GenAI SDK
* **Primary Frontends:**
  * **Primary SaaS App:** High-fidelity single-page HTML/CSS/JS frontend served by FastAPI on port `8000`.
  * **Fallback / Legacy App:** Streamlined, synchronized Streamlit frontend on port `8501`.
* **Database & Security:** Isolated SQLite Multi-Tenant Database with automated profile auto-saving.

---

## 💎 Exquisite Brand Redesign & Features

### 1. Organic Contrast Layout Color System
* Swapped the primary variables to feature a cozy, organic warm beige background (`#E6D7C3`) for the main page layout.
* Created beautiful visual contrast using elegant ivory cream panels (`#FAF5EB`) for cards, login sheets, and the sidebar.
* Input fields, dropdown selects, file dropzones, and messaging bars are rendered in warm beige (`#E6D7C3`) inside ivory cards for a premium, tactile feel.

### 2. Apple-Style Smooth Curves & Design Tokens
* Replaced all default browser sharp edges with strict, relative rounded design tokens in `:root`:
  * `--radius-xl` (`32px`): Auth splash sheets & large cards.
  * `--radius-lg` (`24px`): Chat workspace boxes & curved sidebar right edges.
  * `--radius-md` (`16px`): Buttons, dropzones, & bubble frames.
  * `--radius-sm` (`12px`): Input fields & dropdown selectors.
* Added rounded top-right and bottom-right edges to the sidebar, cleanly wrapping its border line while leaving the left side viewport-flush.

### 3. Elite Typography Pairing
* **Serif Headers (`Cormorant Garamond`)**: All headings (`h1`, `h2`, `h3`) utilize this elegant, classical editorial typeface to establish an expensive " bespoke private advisor" look.
* **Geometric Sans-Serif Body (`Plus Jakarta Sans`)**: Body copy, inputs, menu choices, and chat bubbles use this modern geometric typeface (favored by Stripe & Linear) for supreme legibility.

### 4. Bypassed OTP & Fast Signup Redirection
* Streamlined the onboarding process by completely removing the 6-digit email OTP modal code step.
* **Direct Database Registration**: Modified the `/api/auth/register` POST endpoint to directly save the new user record in the primary database.
* **Sign In Transition**: Bypassing auto-login, successful registration immediately switches the UI to the **Sign In** tab, pre-fills the new username for convenience, and prompts the user to authenticate.

### 5. Clutter-Free Aesthetic & Asset Cleanup
* Removed all visual noise to prioritize clean executive reading:
  * Pruned suggestion quick-start pills from the main workspace.
  * Pruned the `Logged in as: [username]` metadata labels in the sidebar brand header.
  * Removed all rocket emoji `🚀` symbols and logo image files from page titles, headers, and signup sheets.

---

## 🏗️ Technical Architecture
```
User
 ├─► FastAPI Web App (serves frontend/ on Port 8000)
 │    ├─► db_manager.py     (SQLite Multi-Tenant Session Registry)
 │    ├─► gemini_service.py (Gemini API & Failover Engine)
 │    ├─► prompt_manager.py (Bespoke Strategy Persona Prompts)
 │    └─► email_service.py  (Safe ASCII SMTP Fallback Logging)
 │
 └─► Streamlit UI (app.py on Port 8501) - Synchronized layout & aesthetics
```

---

## ⚙️ Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Praneesh-Gattadi/ai-career-advisor-chatbot.git
cd ai-career-advisor-chatbot
```

### 2. Set Up a Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Your Environment Variables
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 5. Start the Services

#### Serve the Primary FastAPI Web Application (Port 8000):
```bash
python main.py
```
Open [http://localhost:8000](http://localhost:8000) in your browser.

#### Serve the Streamlit Application (Port 8501):
```bash
streamlit run app.py
```

---

## ☁️ Production AWS EC2 Deployment
* Runs continuously in the background on the AWS EC2 Linux instance using `nohup` execution wrappers.
* Exposes Port `8000` (FastAPI Web App) and Port `8501` (Streamlit Fallback).
* Guarded by standard Git protections via `.gitignore` to secure localized SQLite credentials and `.env` profiles.