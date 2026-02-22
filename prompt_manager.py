class PromptManager:
    """
    Centralizes all prompt engineering for the Career Advisor chatbot.
    - System prompt defines the assistant's role and constraints
    - build_prompt() assembles the full user prompt with chat history
    - Prompts are configurable and separated from API/UI logic
    """

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
"""
    HISTORY_LIMIT = 10   # Number of recent messages to include for context

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
