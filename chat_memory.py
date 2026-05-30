# ================== chat_memory.py ==================
# Session-based conversation memory management
# Isolated from UI and API layers

import streamlit as st


class ChatMemory:
    """
    Manages session-based multi-turn conversation memory.
    Stores messages in Streamlit's session_state for persistence
    within a single user session.

    Message format: "Role: message content"
    """

    SESSION_KEY = "chat_history"

    @classmethod
    def init(cls):
        """Initialize memory if not already set for this session."""
        if cls.SESSION_KEY not in st.session_state:
            st.session_state[cls.SESSION_KEY] = []

    @classmethod
    def add_message(cls, role: str, message: str):
        """
        Append a new message to the conversation history.

        Args:
            role: "User" or "Assistant"
            message: The message text
        """
        st.session_state[cls.SESSION_KEY].append(f"{role}: {message}")

    @classmethod
    def get_history(cls) -> list:
        """Return full conversation history as a list of strings."""
        return st.session_state.get(cls.SESSION_KEY, [])

    @classmethod
    def get_structured_history(cls) -> list:
        """Return history as list of structured message dicts for Chat APIs."""
        structured = []
        for msg in cls.get_history():
            if ":" in msg:
                role, content = msg.split(":", 1)
                role = role.strip().lower()
                # Map to standard role names: "user" or "assistant"
                api_role = "user" if role == "user" else "assistant"
                structured.append({"role": api_role, "content": content.strip()})
            else:
                structured.append({"role": "user", "content": msg})
        return structured

    @classmethod
    def clear(cls):
        """Reset the conversation history."""
        st.session_state[cls.SESSION_KEY] = []

    @classmethod
    def message_count(cls) -> int:
        """Return number of messages in history."""
        return len(cls.get_history())
