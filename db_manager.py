import sqlite3
import os
import hashlib
import json
from loguru import logger

DB_FILE = os.path.join(os.path.dirname(__file__), "career_coach.db")

class DBManager:
    @staticmethod
    def get_connection():
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def hash_password(password: str) -> str:
        """Hashes a password securely using SHA-256 and a production-grade secret salt."""
        salt = "career_advisor_production_salt_987!"
        return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

    @classmethod
    def init_db(cls):
        """Initializes the multi-tenant SQLite database schema."""
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if old table structure exists without user support, drop to recreate clean production schema
                cursor.execute("PRAGMA table_info(sessions)")
                columns = [row["name"] for row in cursor.fetchall()]
                if columns and "username" not in columns:
                    logger.warning("⚠️ Old database sessions table found. Migrating schema to multi-tenant user isolation...")
                    cursor.execute("DROP TABLE IF EXISTS messages")
                    cursor.execute("DROP TABLE IF EXISTS sessions")
                    cursor.execute("DROP TABLE IF EXISTS users")
                
                # Create users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        email TEXT,
                        password_hash TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Check if email and profile columns exist (migration for existing users table)
                cursor.execute("PRAGMA table_info(users)")
                user_columns = [row["name"] for row in cursor.fetchall()]
                if "email" not in user_columns:
                    logger.info("💼 Migrating users table: adding email column...")
                    cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
                
                # Fetch fresh columns after possible email addition
                cursor.execute("PRAGMA table_info(users)")
                user_columns = [row["name"] for row in cursor.fetchall()]
                for col in ["education", "experience", "target_goal", "resume_text", "resume_filename"]:
                    if col not in user_columns:
                        logger.info(f"💼 Migrating users table: adding {col} column...")
                        cursor.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")

                # Create pending_users table for SMTP verification holding state
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS pending_users (
                        username TEXT PRIMARY KEY,
                        email TEXT NOT NULL,
                        password_hash TEXT NOT NULL,
                        otp TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id TEXT PRIMARY KEY,
                        username TEXT NOT NULL,
                        title TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE
                    )
                """)
                # Create messages table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
                    )
                """)
                # Create quiz results table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS quiz_results (
                        username TEXT PRIMARY KEY,
                        strengths TEXT NOT NULL,
                        environment TEXT NOT NULL,
                        motivation TEXT NOT NULL,
                        persona_report TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE
                    )
                """)
                # Create mock interviews table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS mock_interviews (
                        session_id TEXT PRIMARY KEY,
                        username TEXT NOT NULL,
                        role TEXT NOT NULL,
                        round_num INTEGER DEFAULT 1,
                        chat_history TEXT NOT NULL,
                        scorecard TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE
                    )
                """)
                conn.commit()
                logger.info("✅ Multi-Tenant SQLite Database initialized successfully with Career Guidance Hub schemas")
        except Exception as e:
            logger.error(f"Failed to initialize SQLite DB: {str(e)}")

    @classmethod
    def register_user(cls, username: str, email: str, password: str, password_already_hashed: bool = False) -> bool:
        """Registers a new user after checking for username duplicates."""
        username = username.strip().lower()
        email = email.strip()
        if not username or not password:
            return False
        try:
            password_hash = password if password_already_hashed else cls.hash_password(password)
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                    (username, email, password_hash)
                )
                conn.commit()
                logger.info(f"👤 Registered new user: {username} ({email})")
                return True
        except sqlite3.IntegrityError:
            logger.warning(f"⚠️ Registration rejected: username '{username}' already exists")
            return False
        except Exception as e:
            logger.error(f"Error during registration: {str(e)}")
            return False

    @classmethod
    def save_pending_user(cls, username: str, email: str, password: str, otp: str) -> bool:
        """Stores unverified registration details temporarily pending email verification."""
        username = username.strip().lower()
        email = email.strip()
        if not username or not password or not email or not otp:
            return False
        try:
            password_hash = cls.hash_password(password)
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                # Remove any existing pending registration for this username first
                cursor.execute("DELETE FROM pending_users WHERE username = ?", (username,))
                cursor.execute(
                    "INSERT INTO pending_users (username, email, password_hash, otp) VALUES (?, ?, ?, ?)",
                    (username, email, password_hash, otp)
                )
                conn.commit()
                logger.info(f"⏳ Stored pending registration: {username} ({email})")
                return True
        except Exception as e:
            logger.error(f"Error saving pending user: {str(e)}")
            return False

    @classmethod
    def get_pending_user(cls, username: str) -> dict:
        """Retrieves temporary signup details for validation."""
        username = username.strip().lower()
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM pending_users WHERE username = ?", (username,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error retrieving pending user: {str(e)}")
            return None

    @classmethod
    def delete_pending_user(cls, username: str) -> bool:
        """Removes a pending registration once verified or expired."""
        username = username.strip().lower()
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM pending_users WHERE username = ?", (username,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error deleting pending user: {str(e)}")
            return False

    @classmethod
    def verify_user(cls, username: str, password: str) -> bool:
        """Verifies if username and password hash match."""
        username = username.strip().lower()
        if not username or not password:
            return False
        try:
            password_hash = cls.hash_password(password)
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT password_hash FROM users WHERE username = ?",
                    (username,)
                )
                row = cursor.fetchone()
                if row and row["password_hash"] == password_hash:
                    logger.info(f"🔑 User authenticated successfully: {username}")
                    return True
            logger.warning(f"⚠️ Authentication failed for user: {username}")
            return False
        except Exception as e:
            logger.error(f"Error during verification: {str(e)}")
            return False

    @classmethod
    def create_session(cls, session_id: str, username: str, title: str):
        """Creates a new isolated session linked to a specific user."""
        username = username.strip().lower()
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR IGNORE INTO sessions (id, username, title) VALUES (?, ?, ?)",
                    (session_id, username, title)
                )
                conn.commit()
                logger.info(f"💾 Created private session: {session_id} | user={username} | title={title}")
        except Exception as e:
            logger.error(f"Failed to create private session: {str(e)}")

    @classmethod
    def get_all_sessions(cls, username: str) -> list:
        """Retrieves all sessions belonging to a specific user."""
        username = username.strip().lower()
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, title, created_at FROM sessions WHERE username = ? ORDER BY created_at DESC",
                    (username,)
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to retrieve private sessions for {username}: {str(e)}")
            return []

    @classmethod
    def get_messages(cls, session_id: str) -> list:
        """Retrieves messages of an isolated session."""
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT role, content FROM messages WHERE session_id = ? ORDER BY timestamp ASC",
                    (session_id,)
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to retrieve messages: {str(e)}")
            return []

    @classmethod
    def add_message(cls, session_id: str, role: str, content: str):
        """Appends a message to the database and auto-updates the session title."""
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
                    (session_id, role, content)
                )
                # Auto-update session title based on the first user query
                if role.lower() == "user":
                    cursor.execute(
                        "SELECT COUNT(*) as count FROM messages WHERE session_id = ?",
                        (session_id,)
                    )
                    count = cursor.fetchone()["count"]
                    if count <= 1:
                        title = content[:30] + "..." if len(content) > 30 else content
                        cursor.execute(
                            "UPDATE sessions SET title = ? WHERE id = ?",
                            (title, session_id)
                        )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to add message: {str(e)}")

    @classmethod
    def delete_session(cls, session_id: str):
        """Deletes a session and its associated messages (cascades)."""
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
                conn.commit()
                logger.info(f"🗑️ Deleted private session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to delete session: {str(e)}")

    # ── Career Quiz Results Methods ───────────────────────────────────────────
    @classmethod
    def save_quiz_result(cls, username: str, strengths: str, environment: str, motivation: str, report: str):
        """Saves or updates career quiz results for the user."""
        username = username.strip().lower()
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO quiz_results (username, strengths, environment, motivation, persona_report)
                    VALUES (?, ?, ?, ?, ?)
                """, (username, strengths, environment, motivation, report))
                conn.commit()
                logger.info(f"🧭 Saved Career Quiz results for user: {username}")
        except Exception as e:
            logger.error(f"Failed to save quiz results: {str(e)}")

    @classmethod
    def get_quiz_result(cls, username: str) -> dict:
        """Retrieves career quiz results for the user if they exist."""
        username = username.strip().lower()
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM quiz_results WHERE username = ?", (username,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Failed to retrieve quiz results: {str(e)}")
            return None

    # ── Mock Interview State Methods ──────────────────────────────────────────
    @classmethod
    def save_mock_interview(cls, session_id: str, username: str, role: str, round_num: int, chat_history: list, scorecard: str = None):
        """Saves or updates the turn-by-turn state of an active mock interview session."""
        username = username.strip().lower()
        history_json = json.dumps(chat_history)
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO mock_interviews (session_id, username, role, round_num, chat_history, scorecard)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (session_id, username, role, round_num, history_json, scorecard))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save mock interview: {str(e)}")

    @classmethod
    def get_mock_interview(cls, session_id: str) -> dict:
        """Retrieves mock interview session state from database."""
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM mock_interviews WHERE session_id = ?", (session_id,))
                row = cursor.fetchone()
                if row:
                    data = dict(row)
                    data["chat_history"] = json.loads(data["chat_history"])
                    return data
                return None
        except Exception as e:
            logger.error(f"Failed to retrieve mock interview state: {str(e)}")
            return None

    @classmethod
    def delete_mock_interview(cls, session_id: str):
        """Deletes a mock interview record."""
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM mock_interviews WHERE id = ?", (session_id,))
                conn.commit()
        except Exception as e:
            pass

    @classmethod
    def get_user_profile(cls, username: str) -> dict:
        """Retrieves user profile details from the database."""
        username = username.strip().lower()
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT education, experience, target_goal, resume_text, resume_filename FROM users WHERE username = ?",
                    (username,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Failed to get user profile for {username}: {str(e)}")
            return None

    @classmethod
    def save_user_profile(cls, username: str, education: str, experience: str, target_goal: str, resume_text: str = None, resume_filename: str = None) -> bool:
        """Saves user profile details to the database."""
        username = username.strip().lower()
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                # If resume details are not provided, keep the existing ones
                if resume_text is None:
                    cursor.execute("""
                        UPDATE users 
                        SET education = ?, experience = ?, target_goal = ?
                        WHERE username = ?
                    """, (education, experience, target_goal, username))
                else:
                    cursor.execute("""
                        UPDATE users 
                        SET education = ?, experience = ?, target_goal = ?, resume_text = ?, resume_filename = ?
                        WHERE username = ?
                    """, (education, experience, target_goal, resume_text, resume_filename, username))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to save user profile for {username}: {str(e)}")
            return False
