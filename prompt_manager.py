# ================== prompt_manager.py ==================
# Manages all prompt engineering logic
# Configurable, reusable, and domain-specific


class PromptManager:
    """
    Centralizes all prompt engineering for the Career Advisor chatbot.
    - System prompt defines the assistant's role and constraints
    - build_prompt() assembles the full user prompt with chat history
    - Prompts are configurable and separated from API/UI logic
    """

    # ── System Prompt ──────────────────────────────────────────────────────────
    SYSTEM_PROMPT = """You are an expert Career Advisor AI assistant.

ROLE:
- You help students and working professionals navigate career decisions.
- You are knowledgeable about career paths, in-demand skills, certifications, and industry trends.

RESPONSIBILITIES:
- Suggest suitable career paths based on background and interests
- Recommend skills, tools, and courses to learn
- Provide step-by-step actionable advice
- Share realistic expectations about timelines and effort required
- Be concise, practical, and encouraging

DOMAIN CONSTRAINTS:
- Stay strictly within career guidance topics
- If a question is outside your domain (e.g., recipes, coding bugs, casual chat), politely decline
  and redirect: "I'm specialized in career guidance. Please ask me something career-related!"

RESPONSE FORMAT:
Always structure your responses clearly using the following sections (only include relevant ones):

🎯 Career Path
📚 Skills to Learn
🛠️ Tools & Technologies
📜 Certifications (if applicable)
🚀 Next Steps
⏱️ Realistic Timeline

Keep each section concise. Use bullet points for clarity.

ADDITIONAL FLOWCHART RULE:
- Whenever laying out a learning roadmap, transition path, or step-by-step career milestones, you MUST also generate a simple and clean flowchart using native Mermaid.js syntax block (e.g. ```mermaid \n graph TD \n ... \n ```).
- Define nodes with clear labels in double quotes (e.g. A["Learn SQL"] --> B["Build ML models"]). Keep it to 3-5 key visual milestone steps.
"""

    # ── History limit ──────────────────────────────────────────────────────────
    HISTORY_LIMIT = 10   # Number of recent messages to include for context

    # ── System Prompt Getter ───────────────────────────────────────────────────
    @classmethod
    def get_system_prompt(cls, profile: dict = None, resume_text: str = None) -> str:
        """
        Return the system prompt containing persona, constraints, and dynamic user context.
        """
        base_prompt = cls.SYSTEM_PROMPT
        
        context_parts = []
        
        if profile:
            context_parts.append("## USER PROFILE")
            if profile.get("education"):
                context_parts.append(f"- **Education Level:** {profile['education']}")
            if profile.get("experience"):
                context_parts.append(f"- **Experience Level:** {profile['experience']}")
            if profile.get("target_goal"):
                context_parts.append(f"- **Target Career Goal:** {profile['target_goal']}")
                
        if resume_text:
            context_parts.append("## USER RESUME CONTEXT (Extracted)")
            # Limit resume context length to ensure efficiency
            truncated_resume = resume_text[:6000]
            context_parts.append(truncated_resume)
            context_parts.append("*(Note: Tailor all recommendations to align with or transition from the skills and experiences found in the resume context above.)*")
            
        if context_parts:
            context_str = "\n".join(context_parts)
            return f"{base_prompt}\n\n{context_str}"
            
        return base_prompt

    # ── Message Builder for Native Chat APIs ───────────────────────────────────
    @classmethod
    def build_messages(cls, user_query: str, structured_history: list) -> list:
        """
        Assembles structured messages for standard Gemini APIs.
        Converts 'assistant' roles to 'model' as required by Gemini.

        Args:
            user_query: The latest message from the user.
            structured_history: List of {"role": "user"/"assistant", "content": "..."} dicts.

        Returns:
            A list of formatted message dicts ready for the Gemini SDK.
            Example: [{"role": "user", "content": "..."}, {"role": "model", "content": "..."}]
        """
        messages = []
        recent_history = structured_history[-cls.HISTORY_LIMIT:]
        
        for msg in recent_history:
            role = "user" if msg["role"] == "user" else "model"
            messages.append({"role": role, "content": msg["content"]})
            
        messages.append({"role": "user", "content": user_query})
        return messages

    # ── Legacy Prompt Builder ──────────────────────────────────────────────────
    @classmethod
    def build_prompt(cls, user_query: str, chat_history: list) -> str:
        """
        Assembles the full prompt by combining the system prompt,
        recent conversation history, and the current user question.

        Args:
            user_query: The latest message from the user.
            chat_history: Full list of "Role: message" strings.

        Returns:
            A complete formatted prompt string ready to send to Gemini.
            Note: Prefer using build_messages and get_system_prompt for modern GenAI.
        """
        recent_history = chat_history[-(cls.HISTORY_LIMIT):]
        history_text = "\n".join(recent_history) if recent_history else "No prior conversation."

        return f"""{cls.SYSTEM_PROMPT}

## Conversation History
{history_text}

## Current User Question
{user_query}

## Your Answer
"""
