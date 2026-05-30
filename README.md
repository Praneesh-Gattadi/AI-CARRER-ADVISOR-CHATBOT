# Carrer Coach - Premium AI Career Strategy Hub

A production-ready, enterprise-grade Generative AI Career Advisor chatbot platform. Built on a modular architecture featuring a high-society luxury design system, stateful multi-tenant SQLite session isolation, and real-time Google Gemini grounding.

---

## 📌 Project Overview
**Carrer Coach** (strictly spelled *Carrer Coach*) provides elite, structured career strategy guidance to students, mid-career switchers, and executives. The platform features a high-end bespoke aesthetic paired with a high-speed direct registration and session persistence architecture.

* **Domain:** AI Career Strategy & Bespoke Executive Coaching
* **Model:** Google Gemini GenAI SDK
* **Primary Web App:** High-fidelity single-page HTML/CSS/JS frontend served by FastAPI on port `8000`.
* **Database & Security:** Isolated SQLite Multi-Tenant Database with automated profile auto-saving.

---

## 💎 Exquisite Brand Redesign & Features

### 1. Organic Contrast Layout Color System
* Features a cozy, organic warm beige background (`#E6D7C3`) for the main page layout.
* Uses elegant ivory cream panels (`#FAF5EB`) for cards, login sheets, and the sidebar to create high-end visual contrast.
* Input fields, dropdown selectors, file dropzones, and messaging bars are rendered in warm beige (`#E6D7C3`) inside ivory cards for a premium, tactile feel.

### 2. Stateful Light & Dark Theme Options
* **Splash Screen Toggler**: An absolute-positioned premium toggle button on the login/signup card lets users switch modes before logging in.
* **Chat Header Toggler**: A dedicated theme toggler placed in the main chat header makes switching themes seamless.
* **Zero Visual Flash (IIFE)**: Equipped the frontend with an immediately-invoked execution block to apply the saved theme before the main DOM loads, preventing any disruptive theme flashing.
* **Stateful Cache**: Automatically caches and restores the user's selected mode preference (`career_coach_theme`) in local storage.

### 3. Apple-Style Smooth Curves & Design Tokens
* Replaced all sharp edges with strict, relative rounded design tokens in `:root`:
  * `--radius-xl` (`32px`): Auth splash sheets & large cards.
  * `--radius-lg` (`24px`): Chat workspace boxes & curved sidebar right edges.
  * `--radius-md` (`16px`): Buttons, dropzones, & bubble frames.
  * `--radius-sm` (`12px`): Input fields & dropdown selectors.
* Added rounded top-right and bottom-right edges to the sidebar, cleanly wrapping its border line while leaving the left side viewport-flush.

### 4. Elite Typography Pairing
* **Serif Headers (`Cormorant Garamond`)**: All headings (`h1`, `h2`, `h3`) utilize this elegant, classical editorial serif typeface to establish an expensive, professional editorial look.
* **Geometric Sans-Serif Body (`Plus Jakarta Sans`)**: Body copy, inputs, dropdown menus, and chat bubbles use this modern geometric typeface for supreme legibility.

### 5. Direct Signup & Redirection Flow
* **Direct Database Registration**: Bypasses secondary verification checks to directly save new user records into the primary database on signup.
* **Pre-Filled Sign In Redirect**: Registration automatically redirects the user to the **Sign In** tab, pre-fills their newly created username for convenience, and shows a success alert.

### 6. Minimalist Workspace Layout
* Pruned all visual clutter to prioritize clean, distraction-free reading:
  * Removed quick-start suggestions and empty-state placeholders.
  * Pruned the authenticated user branding displays from the brand header.
  * Removed all rocket emoji symbols and logos for a purely typographical, ultra-high-end aesthetic.

---

## 🏗️ Technical Architecture
```
User
 └─► FastAPI Web App (serves frontend/ on Port 8000)
      ├─► db_manager.py     (SQLite Multi-Tenant Session Registry)
      ├─► gemini_service.py (Gemini API & Failover Engine)
      ├─► prompt_manager.py (Bespoke Strategy Persona Prompts)
      └─► email_service.py  (Safe ASCII SMTP Fallback Logging)
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

### 5. Start the Service
```bash
python main.py
```
Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## ☁️ Production AWS EC2 Deployment
* Runs continuously in the background on the AWS EC2 Linux instance using `nohup` execution wrappers.
* Exposes Port `8000` (FastAPI Web App).
* Guarded by standard Git protections via `.gitignore` to secure localized SQLite credentials and `.env` profiles.