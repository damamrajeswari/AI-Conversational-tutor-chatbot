import streamlit as st
from db_utils import connect_db, register_user, authenticate_user

# Database Connection
conn = connect_db()

# Login Form
st.title("👤 User Login")

email = st.text_input("Email")
password = st.text_input("Password", type="password")

# Create two columns for Login and Register buttons
col1, col2 = st.columns(2)

# Place buttons in the columns
with col1:
    login_btn = st.button("Login")

with col2:
    register_btn = st.button("Register")

# Handle login
if login_btn:
    user = authenticate_user(conn, email, password)
    if user:
        st.session_state["user"] = email  # Store user email in session
        st.success("✅ Login successful! Redirecting to chat...")
        st.switch_page("pages/home.py")   # To redirect to the main app page
    else:
        st.error("🚨 Invalid email or password!")

# Handle registration
if register_btn:
    if email and password:
        if register_user(conn, email, password):
            st.success("✅ Registration successful! Please log in.")
        else:
            st.error("🚨 Email already exists!")
