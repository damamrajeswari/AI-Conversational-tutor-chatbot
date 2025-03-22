import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
import time
import uuid
from db_utils import connect_db, save_chat, get_chat_history, get_user_sessions, get_session_summary, save_new_session
from system_prompt import get_system_prompt

# ✅ Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# ✅ Check if API key is available
if not api_key:
    st.error("🚨 GOOGLE_API_KEY not found. Please check your .env file.")
    st.stop()

# ✅ Configure Google AI
model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)

# ✅ Assign system prompt
SYSTEM_PROMPT = get_system_prompt()

# ✅ Database Connection
conn = connect_db()

# ✅ Check if user is logged in
def check_user_login():
    if "user" not in st.session_state:
        st.warning("🔒 You must log in first!")
        st.stop()

def get_session_id(email):
    if "session_id" not in st.session_state:
        new_session_id = str(uuid.uuid4())  # Generate a unique session ID
        st.session_state["session_id"] = new_session_id  # Store session ID
        save_new_session(conn, email, new_session_id)  # Save session in DB
        st.rerun()
    return st.session_state["session_id"]

def initialize_chat_session(email, session_id):
    if "chat" not in st.session_state:
        st.session_state["chat"] = get_chat_history(conn, email, session_id)  # Fetch from DB

def logout_user():
    st.session_state.clear()  # Clears session properly
    st.warning("You have been logged out. Please refresh the page to log in again.")
    st.stop()

def start_new_chat(email):
    new_session_id = str(uuid.uuid4())  # Generate a unique session ID
    st.session_state["session_id"] = new_session_id  # Store session ID
    save_new_session(conn, email, new_session_id)  # Save session in DB
    st.rerun()  # Refresh UI

def display_session_history(email):
    st.sidebar.title("Previous History")
    sessions = get_user_sessions(conn, email)[::-1]  
    for session_id in sessions:
        session_summary = get_session_summary(conn, session_id)  # Generate session title
        session_key = f"session_{session_id}"
        if st.sidebar.button(f"{session_summary}", key=session_key):
            st.session_state["session_id"] = session_id  # Store selected session
            st.rerun()  # Refresh UI to load chat

def display_chat_history(email):
    if "session_id" in st.session_state:
        session_id = st.session_state["session_id"]
        
        # Fetch chat history from the database
        chat_history = get_chat_history(conn, email, session_id)
        
        # Ensure chat history is available
        if chat_history:
            # Loop through and display previous chat history
            for user_msg, ai_resp in chat_history:
                # Display user message
                with st.chat_message("user"):
                    st.markdown(f"{user_msg}")

                # Display assistant's response
                with st.chat_message("assistant"):
                    st.markdown(f"{ai_resp}")

# ✅ Function to get bot response using conversation history from the database
def get_bot_response(user_input, user_email, session_id, conn):
    # Fetch conversation history from the database
    conversation_history = get_chat_history(conn, user_email, session_id)

    # Format conversation history as a string to include in the prompt
    history_text = ""
    for user_message, ai_response in conversation_history:
        history_text += f"User: {user_message}\nAI: {ai_response}\n"

    # Add the current user input to the conversation context
    history_text += f"User: {user_input}\n"

    # Format the prompt
    prompt_input = f"""
    {SYSTEM_PROMPT}

    You have the following conversation history:

    {history_text}

    Now, user asks:
    {user_input}
    """

    # Call the model with the formatted prompt
    bot_response = model.invoke(prompt_input)  # Use invoke instead of generate

    # Extract response text correctly
    response_text = bot_response.content if hasattr(bot_response, "content") else str(bot_response)

    return response_text

# ✅ Function to process user input and interact with the model
def process_user_input(email):
    user_input = st.chat_input("Type your message...")

    if user_input:
        with st.chat_message("user"):
            st.markdown(f"{user_input}")

        with st.chat_message("assistant"):
            with st.spinner("Generating..."):
                try:
                    # Generate bot response using conversation history from the database
                    bot_response = get_bot_response(user_input, email, st.session_state["session_id"], conn)

                    # Typing effect
                    response_placeholder = st.empty()
                    response_text = ""
                    for char in bot_response:
                        response_text += char
                        response_placeholder.markdown(f"{response_text}")
                        time.sleep(0.01)  # Adjust speed as needed

                    # Save chat to the database
                    save_chat(conn, email, st.session_state["session_id"], user_input, bot_response)

                    # Update session chat history in session state
                    st.session_state["chat"].append((user_input, bot_response))

                except Exception as e:
                    st.error(f"🚨 Error: {e}")

def setup_buttons():
    col3, col4 = st.sidebar.columns([1, 1])  # Equal width columns
    with col3:
        logout = st.button("Logout")  # No need for st.sidebar inside columns

    with col4:
        new = st.button("New Chat")

    return logout, new

# Main Streamlit app flow
def main():
    # Check if user is logged in
    check_user_login()

    email = st.session_state["user"]

    # Get or create session ID
    session_id = get_session_id(email)

    # Initialize chat session
    initialize_chat_session(email, session_id)

    st.title("AI - Data Science Tutor")
    st.write("Ask any Data Science related questions...")

    # Setup Buttons
    logout, new = setup_buttons()

    # Logout Button
    if logout:
        logout_user()

    # New Chat Button
    if new:
        start_new_chat(email)

    # Display session history and chat
    display_session_history(email)
    display_chat_history(email)

    # Process User Input
    process_user_input(email)

# Run the main function
if __name__ == "__main__":
    main()
