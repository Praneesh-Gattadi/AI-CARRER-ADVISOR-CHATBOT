# Carrer Coach — Premium AI Career Strategy Hub

A production-ready, multi-tenant Generative AI Career Strategy platform. Built on an enterprise-grade modular architecture featuring an editorial design system, stateful SQLite isolation, real-time Google Gemini grounding, and interactive roadmap visualization components.

---

## 📌 Features & Visual Architecture

### 1. Organic Contrast Layout Color System
* **Cozy Warm Beige Background (`#E6D7C3`)**: Establishes a comfortable, premium canvas.
* **Ivory Cream Panels (`#FAF5EB`)**: Highlights cards, auth sheets, and context panels with high-end visual contrast.
* **Warm Beige UI Controls**: Input fields, dropdown select dropdowns, drag-and-drop file areas, and chat message bars use organic backgrounds for a premium, tactile interaction system.

### 2. Stateful Light & Dark Theme System
* **Dual Toggles**: Dedicated controls placed in both the splash screen and the chat workspace header.
* **Zero Visual Flash (IIFE)**: Equipped with an immediately-invoked execution script block to load preference values before the main DOM renders, preventing disruptive white flash.
* **Local Storage Cache**: Automatically restores the user's selected mode preference (`career_coach_theme`).

### 3. Apple-Style Design Tokens
* Strictly rounded relative borders using `:root` design tokens:
  * `--radius-xl` (`32px`): Splash auth forms.
  * `--radius-lg` (`24px`): Main chat workspace container.
  * `--radius-md` (`16px`): Primary action buttons and text input areas.
  * `--radius-sm` (`12px`): Input fields, dropdown menus, and text bubble frames.
* Fluid sidebar layout wrapping rounded right edges cleanly.

### 4. Interactive Mermaid.js Roadmap Explorer
* **Viewport Explorer**: Clicking on any flowchart diagram opens a high-fidelity glassmorphic viewer.
* **Interactive Transforms**: Features smooth viewport click-and-drag panning and limits the zoom multiplier between `0.2x` and `5.0x`.
* **Multi-Format Image Downloads**: Direct native downloads of diagrams in vector **SVG** format or high-resolution **PNG** format (respecting current light/dark themes).

### 5. Multi-Format Strategy Export Hub
* Accessible from the main header, allowing users to save their entire conversation logs:
  * **Markdown Format (.md)**: Highly readable, structured documentation.
  * **Enterprise JSON (.json)**: Complete context metadata alongside turn-by-turn chat history.
  * **Bespoke Print-Ready HTML (.html)**: Pre-styled editorial format designed specifically for single-click printing to **PDF** using standard browser printing engines (`Ctrl + P`).

---

## 🏗️ System Architecture

```text
User Workspace
 └─► FastAPI Web App Server (Port 8000)
      ├─► Static Assets (index.html, style.css, app.js)
      ├─► db_manager.py     (Multi-Tenant SQLite isolated database)
      ├─► gemini_service.py (Gemini official GenAI Client with typewriter fallback streaming)
      ├─► prompt_manager.py (Persona prompting context)
      └─► email_service.py  (Safe ASCII SMTP verification logger)
```

---

## ⚙️ Local Installation & Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Praneesh-Gattadi/AI-CARRER-ADVISOR-CHATBOT.git
cd AI-CARRER-ADVISOR-CHATBOT
```

### 2. Configure Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # macOS / Linux
venv\Scripts\activate     # Windows PowerShell
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment variables
Create a `.env` file in the root workspace folder:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 5. Launch the Application
```bash
python main.py
```
Open **[http://localhost:8000](http://localhost:8000)** in your web browser.

---

## ☁️ AWS EC2 Linux Deployment Protocol

The application runs continuously on AWS EC2 servers using background process wrappers.

### 1. Secure Private Key Permissions (Windows PowerShell)
Before connecting via SSH, restrict file permissions:
```powershell
icacls .\chatbot-key.pem /inheritance:r
icacls .\chatbot-key.pem /grant:r "$($env:USERNAME):(R)"
```

### 2. Establish SSH Terminal Connection
```powershell
ssh -i .\chatbot-key.pem ubuntu@54.91.187.103
```

### 3. Sync Changes and Start Server
```bash
cd ai-career-advisor-chatbot
git pull origin main
source venv/bin/activate
nohup python3 main.py > app.log 2>&1 &
```
The server is accessible on Port `8000` (`http://54.91.187.103:8000`).