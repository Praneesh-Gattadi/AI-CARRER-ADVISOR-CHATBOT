/* ================== app.js ================== */

// ── STATE VARIABLES ──────────────────────────────────────────────────────────
let activeUser = localStorage.getItem("career_hub_user") || "";
let activeSessionId = "";
let resumeText = "";
let interviewSessionId = "";
let pendingVerifyUsername = "";
let pendingVerifyEmail = "";

// ── THEME MANAGEMENT ─────────────────────────────────────────────────────────
(function() {
    const currentTheme = localStorage.getItem("career_coach_theme") || "light";
    if (currentTheme === "dark") {
        document.body.classList.add("dark-mode");
    } else {
        document.body.classList.remove("dark-mode");
    }
})();

function toggleTheme() {
    let nextTheme = "light";
    if (document.body.classList.contains("dark-mode")) {
        document.body.classList.remove("dark-mode");
    } else {
        document.body.classList.add("dark-mode");
        nextTheme = "dark";
    }
    localStorage.setItem("career_coach_theme", nextTheme);
    updateThemeToggleIcons(nextTheme);
}

function updateThemeToggleIcons(theme) {
    const mainBtn = document.getElementById("theme-toggle-btn");
    const authBtn = document.getElementById("auth-theme-toggle-btn");
    const iconClass = theme === "dark" ? "fa-solid fa-sun" : "fa-solid fa-moon";
    const titleText = theme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode";
    
    if (mainBtn) {
        mainBtn.innerHTML = `<i class="${iconClass}"></i>`;
        mainBtn.title = titleText;
    }
    if (authBtn) {
        authBtn.innerHTML = `<i class="${iconClass}"></i>`;
        authBtn.title = titleText;
    }
}

// Initialize theme icons on script start
window.addEventListener("DOMContentLoaded", () => {
    const currentTheme = localStorage.getItem("career_coach_theme") || "light";
    updateThemeToggleIcons(currentTheme);
});

// ── DOM ELEMENTS ─────────────────────────────────────────────────────────────
const authContainer = document.getElementById("auth-container");
const appContainer = document.getElementById("app-container");
const globalLoader = document.getElementById("global-loader");
const loaderText = document.getElementById("loader-text");

// ── APP INITIALIZATION ────────────────────────────────────────────────────────
window.addEventListener("DOMContentLoaded", () => {
    setupProfileListeners();
    if (activeUser) {
        showApp();
    } else {
        showAuth();
    }
});

// ── LOADING OVERLAY ──────────────────────────────────────────────────────────
function showLoader(text = "Processing...") {
    loaderText.innerText = text;
    globalLoader.classList.remove("hidden");
}
function hideLoader() {
    globalLoader.classList.add("hidden");
}

// ── AUTHENTICATION FLOWS ──────────────────────────────────────────────────────
function showAuth() {
    authContainer.classList.remove("hidden");
    appContainer.classList.add("hidden");
}

function showApp() {
    authContainer.classList.add("hidden");
    appContainer.classList.remove("hidden");
    const displayEl = document.getElementById("logged-user-display");
    if (displayEl) {
        displayEl.innerText = activeUser;
    }
    
    // Restore profile details of logged user from localStorage
    loadUserProfile();
    
    // Load dynamic elements
    loadSessions();
    
    // Restore sidebar collapse preference
    const isCollapsed = localStorage.getItem("sidebar_collapsed") === "true";
    if (isCollapsed) {
        appContainer.classList.add("sidebar-collapsed");
    } else {
        appContainer.classList.remove("sidebar-collapsed");
    }
}

// ── USER PROFILE PERSISTENCE ──────────────────────────────────────────────────
function setupProfileListeners() {
    const eduSelect = document.getElementById("profile-education");
    const expSelect = document.getElementById("profile-experience");
    const targetInput = document.getElementById("profile-target");
    
    if (eduSelect) {
        eduSelect.addEventListener("change", saveUserProfileOnServer);
    }
    
    if (expSelect) {
        expSelect.addEventListener("change", saveUserProfileOnServer);
    }
    
    if (targetInput) {
        targetInput.addEventListener("change", saveUserProfileOnServer);
        targetInput.addEventListener("blur", saveUserProfileOnServer);
    }
}

async function saveUserProfileOnServer() {
    if (!activeUser) return;
    
    const edu = document.getElementById("profile-education").value;
    const exp = document.getElementById("profile-experience").value;
    const target = document.getElementById("profile-target").value;
    
    // Save to localStorage as a fast local cache
    localStorage.setItem(`career_coach_edu_${activeUser}`, edu);
    localStorage.setItem(`career_coach_exp_${activeUser}`, exp);
    localStorage.setItem(`career_coach_target_${activeUser}`, target);
    
    try {
        await fetch("/api/profile/save", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                username: activeUser,
                education: edu,
                experience: exp,
                target_goal: target
            })
        });
    } catch (e) {
        console.error("Failed to auto-save profile on server", e);
    }
}

async function loadUserProfile() {
    if (!activeUser) return;
    
    // Check localStorage cache first for immediate rendering
    const cachedEdu = localStorage.getItem(`career_coach_edu_${activeUser}`);
    const cachedExp = localStorage.getItem(`career_coach_exp_${activeUser}`);
    const cachedTarget = localStorage.getItem(`career_coach_target_${activeUser}`);
    const cachedResumeFilename = localStorage.getItem(`career_coach_resume_filename_${activeUser}`);
    
    if (cachedEdu) document.getElementById("profile-education").value = cachedEdu;
    if (cachedExp) document.getElementById("profile-experience").value = cachedExp;
    if (cachedTarget) document.getElementById("profile-target").value = cachedTarget;
    
    const statusBox = document.getElementById("resume-status");
    if (cachedResumeFilename) {
        statusBox.innerText = `✅ Parsed successfully! (${cachedResumeFilename})`;
        statusBox.style.background = "rgba(16, 185, 129, 0.08)";
        statusBox.style.color = "#10b981";
        statusBox.style.borderColor = "rgba(16, 185, 129, 0.2)";
        statusBox.classList.remove("hidden");
    }
    
    // Pull authoritative data from server
    try {
        const res = await fetch(`/api/profile?username=${encodeURIComponent(activeUser)}`);
        if (res.ok) {
            const data = await res.json();
            const edu = data.education || "Not specified";
            const exp = data.experience || "Not specified";
            const target = data.target_goal || "";
            resumeText = data.resume_text || "";
            const resumeFilename = data.resume_filename || "";
            
            document.getElementById("profile-education").value = edu;
            document.getElementById("profile-experience").value = exp;
            document.getElementById("profile-target").value = target;
            
            localStorage.setItem(`career_coach_edu_${activeUser}`, edu);
            localStorage.setItem(`career_coach_exp_${activeUser}`, exp);
            localStorage.setItem(`career_coach_target_${activeUser}`, target);
            localStorage.setItem(`career_coach_resume_text_${activeUser}`, resumeText);
            localStorage.setItem(`career_coach_resume_filename_${activeUser}`, resumeFilename);
            
            if (resumeFilename) {
                statusBox.innerText = `✅ Parsed successfully! (${resumeFilename})`;
                statusBox.style.background = "rgba(16, 185, 129, 0.08)";
                statusBox.style.color = "#10b981";
                statusBox.style.borderColor = "rgba(16, 185, 129, 0.2)";
                statusBox.classList.remove("hidden");
            } else {
                statusBox.classList.add("hidden");
                statusBox.innerText = "";
            }
        }
    } catch (e) {
        console.error("Failed to load authoritative profile from server", e);
    }
}

// Ensure the OTP panel is hidden when switching tabs
function switchAuthTab(tab) {
    const btnSignin = document.getElementById("tab-btn-signin");
    const btnSignup = document.getElementById("tab-btn-signup");
    const formSignin = document.getElementById("form-signin");
    const formSignup = document.getElementById("form-signup");
    const formOtp = document.getElementById("form-otp");
    
    if (formOtp) {
        formOtp.style.display = "none";
    }
    
    if (tab === "signin") {
        btnSignin.classList.add("active");
        btnSignup.classList.remove("active");
        formSignin.classList.add("active");
        formSignup.classList.remove("active");
    } else {
        btnSignin.classList.remove("active");
        btnSignup.classList.add("active");
        formSignin.classList.remove("active");
        formSignup.classList.add("active");
    }
    clearAuthAlert();
}

function showAuthAlert(text) {
    const alertBox = document.getElementById("auth-alert");
    alertBox.innerText = text;
    alertBox.classList.remove("hidden");
}
function clearAuthAlert() {
    document.getElementById("auth-alert").classList.add("hidden");
}

async function handleSignIn() {
    const usernameInput = document.getElementById("signin-username").value.trim();
    const passwordInput = document.getElementById("signin-password").value;
    
    if (!usernameInput || !passwordInput) {
        showAuthAlert("Username and password are required.");
        return;
    }
    
    showLoader("Authenticating...");
    try {
        const res = await fetch("/api/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: usernameInput, password: passwordInput })
        });
        
        const data = await res.json();
        if (res.ok) {
            activeUser = data.username;
            localStorage.setItem("career_hub_user", activeUser);
            showApp();
        } else {
            showAuthAlert(data.detail || "Authentication failed.");
        }
    } catch (e) {
        showAuthAlert("Failed to connect to backend server.");
    } finally {
        hideLoader();
    }
}

async function handleSignUp() {
    const usernameInput = document.getElementById("signup-username").value.trim();
    const emailInput = document.getElementById("signup-email").value.trim();
    const passwordInput = document.getElementById("signup-password").value;
    const passwordConfirm = document.getElementById("signup-password-confirm").value;
    
    if (!usernameInput || !emailInput || !passwordInput) {
        showAuthAlert("Username, email, and password are required.");
        return;
    }
    
    // Client-side quick email pattern check
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(emailInput)) {
        showAuthAlert("Invalid email address format.");
        return;
    }
    
    if (passwordInput !== passwordConfirm) {
        showAuthAlert("Passwords do not match.");
        return;
    }
    
    // Client-side password validation
    if (passwordInput.length < 8) {
        showAuthAlert("Password must be at least 8 characters long.");
        return;
    }
    if (!/[A-Z]/.test(passwordInput)) {
        showAuthAlert("Password must contain at least one uppercase letter.");
        return;
    }
    if (!/[a-z]/.test(passwordInput)) {
        showAuthAlert("Password must contain at least one lowercase letter.");
        return;
    }
    if (!/\d/.test(passwordInput)) {
        showAuthAlert("Password must contain at least one number.");
        return;
    }
    if (!/[!@#$%^&*(),.?\":{}|<>]/.test(passwordInput)) {
        showAuthAlert("Password must contain at least one special character.");
        return;
    }
    
    showLoader("Initiating registration...");
    try {
        const res = await fetch("/api/auth/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: usernameInput, email: emailInput, password: passwordInput })
        });
        
        const data = await res.json();
        if (res.ok && data.status === "registered") {
            // Clear signup forms
            document.getElementById("signup-username").value = "";
            document.getElementById("signup-email").value = "";
            document.getElementById("signup-password").value = "";
            document.getElementById("signup-password-confirm").value = "";
            
            // Redirect to Sign In tab
            switchAuthTab("signin");
            
            // Pre-fill the username for convenience
            document.getElementById("signin-username").value = data.username;
            
            showAuthAlert("Account created successfully! Please sign in with your credentials.");
        } else {
            showAuthAlert(data.detail || "Registration failed.");
        }
    } catch (e) {
        showAuthAlert("Failed to connect to server.");
    } finally {
        hideLoader();
    }
}

async function handleVerifyOTP() {
    const otpCode = document.getElementById("otp-code").value.trim();
    if (!otpCode || otpCode.length !== 6) {
        showAuthAlert("Please enter a valid 6-digit verification code.");
        return;
    }
    
    showLoader("Verifying code...");
    try {
        const res = await fetch("/api/auth/verify-otp", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: pendingVerifyUsername, otp: otpCode })
        });
        
        const data = await res.json();
        if (res.ok) {
            activeUser = data.username;
            localStorage.setItem("career_hub_user", activeUser);
            
            // Success transition
            document.getElementById("form-otp").style.display = "none";
            document.getElementById("signup-username").value = "";
            document.getElementById("signup-email").value = "";
            document.getElementById("signup-password").value = "";
            document.getElementById("signup-password-confirm").value = "";
            switchAuthTab("signin");
            showApp();
        } else {
            showAuthAlert(data.detail || "Verification failed. Please check code and retry.");
        }
    } catch (e) {
        showAuthAlert("Failed to connect to server.");
    } finally {
        hideLoader();
    }
}

async function handleResendOTP() {
    if (!pendingVerifyUsername) {
        showAuthAlert("No active registration found. Please try sign up again.");
        return;
    }
    
    showLoader("Resending verification code...");
    try {
        const res = await fetch("/api/auth/resend-otp", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: pendingVerifyUsername })
        });
        
        const data = await res.json();
        if (res.ok) {
            showAuthAlert(`A new verification code has been sent to ${pendingVerifyEmail}.`);
        } else {
            showAuthAlert(data.detail || "Failed to resend code.");
        }
    } catch (e) {
        showAuthAlert("Failed to connect to server.");
    } finally {
        hideLoader();
    }
}

function cancelOTPFlow() {
    document.getElementById("form-otp").style.display = "none";
    document.getElementById("form-signup").classList.add("active");
    document.getElementById("tab-btn-signup").classList.add("active");
    document.getElementById("tab-btn-signin").classList.remove("active");
    clearAuthAlert();
}

function handleLogOut() {
    activeUser = "";
    activeSessionId = "";
    resumeText = "";
    localStorage.removeItem("career_hub_user");
    
    // Clear forms
    document.getElementById("signin-username").value = "";
    document.getElementById("signin-password").value = "";
    document.getElementById("signup-username").value = "";
    document.getElementById("signup-password").value = "";
    document.getElementById("signup-password-confirm").value = "";
    
    // Clear profile in DOM
    const eduSelect = document.getElementById("profile-education");
    const expSelect = document.getElementById("profile-experience");
    const targetInput = document.getElementById("profile-target");
    if (eduSelect) eduSelect.value = "Not specified";
    if (expSelect) expSelect.value = "Not specified";
    if (targetInput) targetInput.value = "";
    
    // Clear status
    document.getElementById("resume-status").classList.add("hidden");
    document.getElementById("resume-status").innerText = "";
    document.getElementById("resume-file-input").value = "";
    
    showAuth();
}



// ── SIDEBAR RESUME UPLOADER ──────────────────────────────────────────────────
function triggerFileInput() {
    document.getElementById("resume-file-input").click();
}

async function handleResumeUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const statusBox = document.getElementById("resume-status");
    statusBox.innerText = "⏳ Uploading...";
    statusBox.classList.remove("hidden");
    statusBox.style.background = "rgba(255, 255, 255, 0.05)";
    statusBox.style.color = "var(--text-muted)";
    statusBox.style.borderColor = "var(--border-color)";
    
    const formData = new FormData();
    formData.append("file", file);
    
    try {
        const res = await fetch(`/api/resume/upload?username=${encodeURIComponent(activeUser)}`, {
            method: "POST",
            body: formData
        });
        
        const data = await res.json();
        if (res.ok) {
            resumeText = data.text;
            statusBox.innerText = `✅ Parsed successfully! (${file.name})`;
            statusBox.style.background = "rgba(16, 185, 129, 0.08)";
            statusBox.style.color = "#10b981";
            statusBox.style.borderColor = "rgba(16, 185, 129, 0.2)";
            
            // Save in localStorage for persistence
            if (activeUser) {
                localStorage.setItem(`career_coach_resume_text_${activeUser}`, resumeText);
                localStorage.setItem(`career_coach_resume_filename_${activeUser}`, file.name);
            }
        } else {
            statusBox.innerText = `❌ Error: ${data.detail}`;
            statusBox.style.background = "rgba(239, 68, 68, 0.08)";
            statusBox.style.color = "#ef4444";
            statusBox.style.borderColor = "rgba(239, 68, 68, 0.2)";
        }
    } catch (e) {
        statusBox.innerText = "❌ Network parse failed.";
        statusBox.style.background = "rgba(239, 68, 68, 0.08)";
        statusBox.style.color = "#ef4444";
        statusBox.style.borderColor = "rgba(239, 68, 68, 0.2)";
    }
}

// ── CHAT MULTI-TENANT SESSIONS ────────────────────────────────────────────────
async function loadSessions() {
    try {
        const res = await fetch(`/api/sessions?username=${encodeURIComponent(activeUser)}`);
        const data = await res.json();
        
        const select = document.getElementById("session-select");
        select.innerHTML = "";
        
        if (data.sessions && data.sessions.length > 0) {
            data.sessions.forEach(s => {
                const opt = document.createElement("option");
                opt.value = s.id;
                opt.innerText = s.title;
                select.appendChild(opt);
            });
            
            // Auto select active session if valid, otherwise first option
            const ids = data.sessions.map(s => s.id);
            if (!activeSessionId || !ids.includes(activeSessionId)) {
                activeSessionId = ids[0];
            }
            select.value = activeSessionId;
            loadMessages();
        } else {
            // If no sessions, automatically create one
            await handleNewSession();
        }
    } catch (e) {
        console.error("Failed to load sessions", e);
    }
}

async function handleNewSession() {
    showLoader("Creating new chat...");
    try {
        const res = await fetch("/api/sessions/create", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: activeUser })
        });
        const data = await res.json();
        if (res.ok) {
            activeSessionId = data.session_id;
            await loadSessions();
        }
    } catch (e) {
        console.error("Failed to create new session", e);
    } finally {
        hideLoader();
    }
}

async function handleDeleteSession() {
    if (!activeSessionId) return;
    if (!confirm("Are you sure you want to delete this session?")) return;
    
    showLoader("Deleting chat...");
    try {
        const res = await fetch(`/api/sessions/delete?session_id=${encodeURIComponent(activeSessionId)}`, {
            method: "DELETE"
        });
        if (res.ok) {
            activeSessionId = "";
            await loadSessions();
        }
    } catch (e) {
        console.error("Failed to delete session", e);
    } finally {
        hideLoader();
    }
}

function switchSession(sessionId) {
    activeSessionId = sessionId;
    loadMessages();
}

async function loadMessages() {
    if (!activeSessionId) return;
    try {
        const res = await fetch(`/api/chat/messages?session_id=${encodeURIComponent(activeSessionId)}`);
        const data = await res.json();
        
        const box = document.getElementById("chat-messages-box");
        box.innerHTML = "";
        
        if (data.messages && data.messages.length > 0) {
            data.messages.forEach(msg => {
                const bubble = document.createElement("div");
                bubble.classList.add("chat-bubble", msg.role.toLowerCase());
                bubble.innerHTML = parseMarkdown(msg.content);
                box.appendChild(bubble);
            });
            // Render Mermaid for historical messages
            renderMermaidInElement(box);
        } else {
            // Empty chat splash welcome
            box.innerHTML = `
                <div class="chat-bubble assistant">
                    👋 Welcome! Ask a career strategy query or select a historical session in the sidebar to begin!
                </div>
            `;
        }
        
        // Scroll bottom
        box.scrollTop = box.scrollHeight;
    } catch (e) {
        console.error("Failed to load messages", e);
    }
}

// ── SENDING CHAT MESSAGES ─────────────────────────────────────────────────────
function handleChatKeyPress(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        submitChatMessage();
    }
}

async function submitChatMessage() {
    const input = document.getElementById("chat-input-field");
    const val = input.value.trim();
    if (!val) return;
    
    // Clear input
    input.value = "";
    
    // Optimistically render user message
    const box = document.getElementById("chat-messages-box");
    const uBubble = document.createElement("div");
    uBubble.classList.add("chat-bubble", "user");
    uBubble.innerText = val;
    box.appendChild(uBubble);
    box.scrollTop = box.scrollHeight;
    
    // Profile info
    const edu = document.getElementById("profile-education").value;
    const exp = document.getElementById("profile-experience").value;
    const goal = document.getElementById("profile-target").value;
    
    // Append loading assistant bubble
    const aBubble = document.createElement("div");
    aBubble.classList.add("chat-bubble", "assistant");
    aBubble.innerHTML = `<span class="streaming-loading"><span class="dot">.</span><span class="dot">.</span><span class="dot">.</span></span>`;
    box.appendChild(aBubble);
    box.scrollTop = box.scrollHeight;
    
    try {
        const res = await fetch("/api/chat/send", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                session_id: activeSessionId,
                username: activeUser,
                message: val,
                education: edu,
                experience: exp,
                target_goal: goal,
                resume_text: resumeText
            })
        });
        
        if (!res.ok) {
            let errorText = "Failed to generate response";
            try {
                const errData = await res.json();
                errorText = errData.detail || errorText;
            } catch (jsonErr) {}
            aBubble.innerHTML = `⚠️ **Backend Error:** ${errorText}`;
            box.scrollTop = box.scrollHeight;
            return;
        }
        
        // Read the stream
        const reader = res.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let accumulatedText = "";
        let isFirstChunk = true;
        
        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value, { stream: true });
            accumulatedText += chunk;
            
            if (isFirstChunk && accumulatedText.trim()) {
                isFirstChunk = false;
                aBubble.innerHTML = "";
            }
            
            aBubble.innerHTML = parseMarkdown(accumulatedText);
            box.scrollTop = box.scrollHeight;
        }
        
        // Finalize formatting and render any Mermaid diagrams
        aBubble.innerHTML = parseMarkdown(accumulatedText);
        await renderMermaidInElement(aBubble);
        box.scrollTop = box.scrollHeight;
        
    } catch (e) {
        console.error(e);
        aBubble.innerHTML = `⚠️ **Connection Error:** Failed to stream response.`;
        box.scrollTop = box.scrollHeight;
    }
}




// ── DOWNLOAD ROADMAP REPORT (MULTI-FORMAT EXPORT HUB) ────────────────────────
function exportRoadmapReport() {
    const box = document.getElementById("chat-messages-box");
    const bubbles = box.querySelectorAll(".chat-bubble");
    if (bubbles.length === 0) {
        alert("Your career roadmap chat is empty! Chat with the strategist first.");
        return;
    }
    
    const modal = document.getElementById("export-modal");
    modal.classList.remove("hidden");
}

function closeExportModal(event) {
    const modal = document.getElementById("export-modal");
    modal.classList.add("hidden");
}

function triggerExport(format) {
    const box = document.getElementById("chat-messages-box");
    const bubbles = box.querySelectorAll(".chat-bubble");
    
    if (format === 'markdown') {
        let reportText = `# Personalized AI Career Strategy Roadmap\n\n`;
        reportText += `Generated on: ${new Date().toLocaleDateString()}\n`;
        reportText += `User Profile Scope: ${activeUser}\n`;
        reportText += `==============================================\n\n`;
        
        bubbles.forEach((b, idx) => {
            const role = b.classList.contains("user") ? "User" : "Strategist";
            reportText += `### [${role}] Block ${idx + 1}\n\n`;
            reportText += b.innerText + "\n\n";
        });
        
        const blob = new Blob([reportText], { type: "text/markdown;charset=utf-8;" });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = `career_roadmap_${activeUser}.md`;
        link.style.display = "none";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } 
    else if (format === 'json') {
        const edu = document.getElementById("profile-education").value;
        const exp = document.getElementById("profile-experience").value;
        const goal = document.getElementById("profile-target").value;
        
        const sessionData = {
            metadata: {
                username: activeUser,
                export_date: new Date().toISOString(),
                user_context: {
                    education: edu,
                    experience: exp,
                    target_goal: goal,
                    has_resume: !!resumeText
                }
            },
            messages: []
        };
        
        bubbles.forEach((b, idx) => {
            const role = b.classList.contains("user") ? "user" : "assistant";
            sessionData.messages.push({
                index: idx + 1,
                role: role,
                content: b.innerText
            });
        });
        
        const jsonString = JSON.stringify(sessionData, null, 4);
        const blob = new Blob([jsonString], { type: "application/json;charset=utf-8;" });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = `career_roadmap_${activeUser}.json`;
        link.style.display = "none";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } 
    else if (format === 'html') {
        const edu = document.getElementById("profile-education").value;
        const exp = document.getElementById("profile-experience").value;
        const goal = document.getElementById("profile-target").value;
        
        let htmlContent = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Career Strategy Roadmap Report - ${activeUser}</title>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #FAF5EB;
            --text: #2E251B;
            --primary: #A18262;
            --border: rgba(107, 85, 56, 0.15);
        }
        body {
            background-color: #FFFFFF;
            color: var(--text);
            font-family: 'Plus Jakarta Sans', sans-serif;
            margin: 0;
            padding: 40px;
            line-height: 1.6;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        header {
            border-bottom: 2px solid var(--primary);
            padding-bottom: 20px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
        }
        h1 {
            font-family: 'Cormorant Garamond', serif;
            font-size: 2.2rem;
            margin: 0 0 10px 0;
            color: var(--text);
        }
        .meta-info {
            font-size: 0.9rem;
            color: #736555;
            display: flex;
            gap: 20px;
            margin-bottom: 10px;
        }
        .section-title {
            font-family: 'Cormorant Garamond', serif;
            font-size: 1.6rem;
            border-bottom: 1px solid var(--border);
            padding-bottom: 6px;
            margin-top: 35px;
            color: var(--primary);
        }
        .context-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .context-table th, .context-table td {
            border: 1px solid var(--border);
            padding: 12px;
            text-align: left;
            font-size: 0.9rem;
        }
        .context-table th {
            background-color: var(--bg);
            font-weight: 600;
            width: 30%;
        }
        .message-bubble {
            margin-bottom: 24px;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid var(--border);
        }
        .message-bubble.user {
            background-color: var(--bg);
            border-left: 4px solid var(--primary);
        }
        .message-bubble.assistant {
            background-color: #FFFFFF;
            border-left: 4px solid #7A8568;
        }
        .bubble-role {
            font-weight: 600;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
            color: var(--primary);
        }
        .bubble-role.assistant {
            color: #7A8568;
        }
        .print-btn {
            background: #A18262;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 0.9rem;
            font-family: inherit;
            font-weight: 600;
            border-radius: 6px;
            cursor: pointer;
            transition: 0.2s ease;
        }
        .print-btn:hover {
            background: #705336;
        }
        @media print {
            .print-btn {
                display: none;
            }
            body {
                padding: 0;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>AI Career Strategy Roadmap Report</h1>
                <div class="meta-info">
                    <span><strong>User:</strong> ${activeUser}</span>
                    <span><strong>Date:</strong> ${new Date().toLocaleDateString()}</span>
                </div>
            </div>
            <button class="print-btn" onclick="window.print()">Print to PDF</button>
        </header>
        
        <h2 class="section-title">Advisor Context</h2>
        <table class="context-table">
            <tr>
                <th>Education Level</th>
                <td>${edu}</td>
            </tr>
            <tr>
                <th>Experience Level</th>
                <td>${exp}</td>
            </tr>
            <tr>
                <th>Target Goal / Role</th>
                <td>${goal || 'Not specified'}</td>
            </tr>
            <tr>
                <th>Resume Text</th>
                <td>${resumeText ? 'Uploaded & Analyzed' : 'No Resume Provided'}</td>
            </tr>
        </table>
        
        <h2 class="section-title">Strategic Conversation</h2>
        <div class="conversation-log">`;
        
        bubbles.forEach((b, idx) => {
            const role = b.classList.contains("user") ? "user" : "assistant";
            const roleTitle = role === "user" ? "User Strategy Inquiry" : "Bespoke Strategic Feedback";
            htmlContent += `
            <div class="message-bubble ${role}">
                <div class="bubble-role ${role}">${roleTitle}</div>
                <div class="bubble-content">${b.innerHTML}</div>
            </div>`;
        });
        
        htmlContent += `
        </div>
    </div>
</body>
</html>`;
        
        const blob = new Blob([htmlContent], { type: "text/html;charset=utf-8;" });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = `career_roadmap_${activeUser}.html`;
        link.style.display = "none";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    closeExportModal();
}



// ── CUSTOM HTML MARKDOWN PARSER ──────────────────────────────────────────────
function parseMarkdown(text) {
    if (!text) return "";
    
    // Escape standard HTML tags
    let html = text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    
    const blocks = [];
    
    // Extract closed mermaid blocks first
    html = html.replace(/```mermaid\s*([\s\S]*?)\s*```/g, function(match, code) {
        const decodedCode = code.replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
        const placeholder = `__BLOCK_PLACEHOLDER_${blocks.length}__`;
        blocks.push(`<div class="mermaid-block"><pre class="mermaid">${decodedCode.trim()}</pre></div>`);
        return placeholder;
    });
    
    // Extract standard closed code blocks
    html = html.replace(/```(\w*)\s*([\s\S]*?)\s*```/g, function(match, lang, code) {
        const placeholder = `__BLOCK_PLACEHOLDER_${blocks.length}__`;
        blocks.push(`<pre class="code-block"><code class="${lang}">${code.trim()}</code></pre>`);
        return placeholder;
    });
    
    // Bold formatting: **text**
    html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    
    // Inline code: `code`
    html = html.replace(/`(.*?)`/g, "<code>$1</code>");
    
    // Bullet list formatting: * or - followed by space
    html = html.split('\n').map(line => {
        const cleanLine = line.trim();
        if (cleanLine.startsWith('- ') || cleanLine.startsWith('* ')) {
            return `<li>${cleanLine.substring(2)}</li>`;
        }
        return line;
    }).join('\n');
    
    // Wrap groups of <li> in <ul>
    html = html.replace(/(<li>[\s\S]*?<\/li>)+/g, '<ul>$&</ul>');
    
    // Replace remaining newlines with <br>
    html = html.replace(/\n/g, "<br>");
    
    // Restore raw code blocks
    blocks.forEach((block, idx) => {
        html = html.replace(`__BLOCK_PLACEHOLDER_${idx}__`, block);
    });
    
    return html;
}

// ── MODERN MERMAID.JS RENDERER ────────────────────────────────────────────────
async function renderMermaidInElement(container) {
    if (typeof mermaid === "undefined") return;
    
    const elements = container.querySelectorAll(".mermaid");
    if (elements.length === 0) return;
    
    try {
        await mermaid.run({
            nodes: elements
        });
        
        // Dynamic click listeners for roadmap exploration modal trigger
        const blocks = container.querySelectorAll(".mermaid-block");
        blocks.forEach(block => {
            if (!block.dataset.hasClickListener) {
                block.dataset.hasClickListener = "true";
                block.addEventListener("click", () => {
                    const svg = block.querySelector("svg");
                    if (svg) {
                        openMermaidExplorer(svg.outerHTML);
                    }
                });
            }
        });
    } catch (err) {
        console.error("Mermaid execution error:", err);
    }
}

// ── SIDEBAR EXPAND/COLLAPSE HANDLER ──────────────────────────────────────────
function toggleSidebar() {
    const workspace = document.getElementById("app-container");
    workspace.classList.toggle("sidebar-collapsed");
    
    // Save the preference in localStorage so it persists across reloads!
    const isCollapsed = workspace.classList.contains("sidebar-collapsed");
    localStorage.setItem("sidebar_collapsed", isCollapsed ? "true" : "false");
}

// ── MERMAID EXPLORER & VIEWPORT TRANSFORMS ────────────────────────────────────
let mermaidZoomScale = 1.0;
let mermaidPanX = 0;
let mermaidPanY = 0;
let isMermaidPanning = false;
let mermaidStartX = 0;
let mermaidStartY = 0;
let currentSvgMarkup = "";

function openMermaidExplorer(svgMarkup) {
    const modal = document.getElementById("mermaid-modal");
    const wrapper = document.getElementById("mermaid-canvas-wrapper");
    
    currentSvgMarkup = svgMarkup;
    wrapper.innerHTML = svgMarkup;
    
    const svgEl = wrapper.querySelector("svg");
    if (svgEl) {
        svgEl.removeAttribute("width");
        svgEl.removeAttribute("height");
        svgEl.style.width = "100%";
        svgEl.style.height = "100%";
    }
    
    mermaidZoomScale = 1.0;
    mermaidPanX = 0;
    mermaidPanY = 0;
    updateMermaidTransform();
    
    modal.classList.remove("hidden");
}

function closeMermaidModal(event) {
    const modal = document.getElementById("mermaid-modal");
    modal.classList.add("hidden");
}

function updateMermaidTransform() {
    const wrapper = document.getElementById("mermaid-canvas-wrapper");
    wrapper.style.transform = `translate(${mermaidPanX}px, ${mermaidPanY}px) scale(${mermaidZoomScale})`;
}

function zoomMermaid(factor) {
    mermaidZoomScale *= factor;
    mermaidZoomScale = Math.max(0.2, Math.min(5.0, mermaidZoomScale));
    updateMermaidTransform();
}

function resetMermaid() {
    mermaidZoomScale = 1.0;
    mermaidPanX = 0;
    mermaidPanY = 0;
    updateMermaidTransform();
}

function startMermaidPan(event) {
    isMermaidPanning = true;
    const viewport = document.getElementById("mermaid-viewport");
    viewport.style.cursor = "grabbing";
    
    mermaidStartX = event.clientX - mermaidPanX;
    mermaidStartY = event.clientY - mermaidPanY;
}

function dragMermaidPan(event) {
    if (!isMermaidPanning) return;
    event.preventDefault();
    
    mermaidPanX = event.clientX - mermaidStartX;
    mermaidPanY = event.clientY - mermaidStartY;
    updateMermaidTransform();
}

function stopMermaidPan() {
    if (!isMermaidPanning) return;
    isMermaidPanning = false;
    const viewport = document.getElementById("mermaid-viewport");
    viewport.style.cursor = "grab";
}

// ── ROADMAP VECTOR & RASTER DOWNLOAD DIRECTIVES ──────────────────────────────
function downloadMermaidSVG() {
    if (!currentSvgMarkup) return;
    
    const blob = new Blob([currentSvgMarkup], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement("a");
    link.href = url;
    link.download = `career_roadmap_${activeUser || "user"}.svg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

function downloadMermaidPNG() {
    if (!currentSvgMarkup) return;
    
    const svgWrapper = document.getElementById("mermaid-canvas-wrapper");
    const svgEl = svgWrapper.querySelector("svg");
    if (!svgEl) return;
    
    const bbox = svgEl.getBoundingClientRect();
    const width = svgEl.viewBox?.baseVal?.width || bbox.width || 800;
    const height = svgEl.viewBox?.baseVal?.height || bbox.height || 600;
    
    const svgString = new XMLSerializer().serializeToString(svgEl);
    const svgBlob = new Blob([svgString], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(svgBlob);
    
    const image = new Image();
    image.onload = function() {
        const canvas = document.createElement("canvas");
        const scale = 2; 
        canvas.width = width * scale;
        canvas.height = height * scale;
        
        const ctx = canvas.getContext("2d");
        const isDark = document.body.classList.contains("dark-mode");
        ctx.fillStyle = isDark ? "#1D1E22" : "#FAF5EB";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.scale(scale, scale);
        ctx.drawImage(image, 0, 0, width, height);
        
        const pngUrl = canvas.toDataURL("image/png");
        const link = document.createElement("a");
        link.href = pngUrl;
        link.download = `career_roadmap_${activeUser || "user"}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    };
    image.onerror = function() {
        alert("Failed to render diagram as PNG.");
        URL.revokeObjectURL(url);
    };
    image.src = url;
}
