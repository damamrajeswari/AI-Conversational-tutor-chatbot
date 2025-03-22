import sqlite3
import hashlib
import uuid
import datetime  # For generating unique session IDs

# ✅ Connect to the database (Creates if it doesn't exist)
def connect_db():
    return sqlite3.connect("users.db", check_same_thread=False)

# ✅ Initialize database and create tables
def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL
                      )''')

    # Create chat history table
    cursor.execute('''CREATE TABLE IF NOT EXISTS chat_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_email TEXT NOT NULL,
                        session_id TEXT NOT NULL,
                        user_message TEXT NOT NULL,
                        ai_response TEXT NOT NULL,
                        FOREIGN KEY(user_email) REFERENCES users(email)
                      )''')

    conn.commit()
    conn.close()

# ✅ Hash passwords before storing (For security)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ✅ Register a new user
def register_user(conn, email, password):
    try:
        cursor = conn.cursor()
        hashed_pw = hash_password(password)
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_pw))
        conn.commit()
    except sqlite3.IntegrityError:
        return False  # Email already exists
    return True  # Registration successful

# ✅ Authenticate user login
def authenticate_user(conn, email, password):
    cursor = conn.cursor()
    hashed_pw = hash_password(password)
    cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, hashed_pw))
    user = cursor.fetchone()
    return user is not None

# ✅ Retrieve chat history for a user
def get_chat_history(conn, user_email, session_id):
    cursor = conn.cursor()
    cursor.execute("SELECT user_message, ai_response FROM chat_history WHERE user_email = ? AND session_id = ?",
                   (user_email, session_id))
    chats = cursor.fetchall()
    return chats  # Return a list of tuples (user_message, ai_response)

# Modify the get_user_sessions function to return a list of session IDs
def get_user_sessions(conn, email):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT session_id FROM chat_history WHERE user_email = ?", (email,))
        sessions = cursor.fetchall()  # This will return a list of session tuples (session_id,)
        return [session[0] for session in sessions]  # Extract session IDs from tuples
    except Exception as e:
        print(f"🚨 Database Error in get_user_sessions: {e}")
        return []  # Return an empty list if there is an error


# def get_session_summary(conn, session_id):
#     cursor = conn.cursor()
#     cursor.execute("SELECT user_message, ai_response FROM chat_history WHERE session_id = ?", (session_id,))
#     chat_history = cursor.fetchall()

#     if not chat_history:
#         return "Empty Session"

#     # Extract the first user message and the last AI response
#     first_message = chat_history[0][0]  # First user message
#     last_response = chat_history[-1][1]  # Last AI response

#     # Generate a short title (max 5-6 words)
#     if len(first_message.split()) <= 8:
#         title = first_message  # Use first user message if it's short
#     else:
#         title = " ".join(first_message.split()[:7]) + "..."  # Trim if too long

#     return title

def get_session_summary(conn, session_id, char_limit=35):
    cursor = conn.cursor()
    cursor.execute("SELECT user_message, ai_response FROM chat_history WHERE session_id = ?", (session_id,))
    chat_history = cursor.fetchall()

    if not chat_history:
        return "Empty Session"

    first_message = chat_history[0][0]  # First user message
    last_response = chat_history[-1][1]  # Last AI response

    title = first_message[:char_limit]  # Start with first user message

    if len(title) < char_limit:  # If it's too short, add from last AI response
        remaining_chars = char_limit - len(title)
        title += " " + last_response[:remaining_chars] if last_response else ""

    return title[:char_limit]  # Ensure it doesn't exceed the limit



# ✅ Store chat history in the database
def save_chat(conn, user_email, session_id, user_message, ai_response):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_history (user_email, session_id, user_message, ai_response) VALUES (?, ?, ?, ?)",
                   (user_email, session_id, user_message, ai_response))
    conn.commit()
def get_last_session(conn, email):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(session_id) FROM chat_history WHERE user_email = ?", (email,))
        last_session = cursor.fetchone()[0]  # Get the last session ID
        return last_session if last_session is not None else 0  # Return 0 if no sessions exist
    except Exception as e:
        print(f"🚨 Database Error in get_last_session: {e}")
        return 0  # Default to 0 in case of error

def save_new_session(conn, email, new_session_id):
    """
    Function to save a new session to the database. Inserts session metadata
    such as session_id, user email, and session start time into the 'sessions' table.
    """
    cursor = conn.cursor()

    # Create the 'sessions' table if it does not exist (you may already have this from earlier)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_email TEXT NOT NULL,
            start_time DATETIME NOT NULL,
            FOREIGN KEY(user_email) REFERENCES users(email)
        )
    """)

    # Insert the new session metadata into the 'sessions' table
    cursor.execute("""
        INSERT INTO sessions (session_id, user_email, start_time)
        VALUES (?, ?, ?)
    """, (new_session_id, email, str(datetime.datetime.now())))

    conn.commit()  # Commit the transaction to save the session
    cursor.close()
    print(f"New session {new_session_id} for user {email} has been saved.")

