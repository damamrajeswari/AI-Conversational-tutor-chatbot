import streamlit as st

# Page Title
st.title("About Me")

# Your Details
st.write("""
👋 Hi, I'm Rajeswari Damam, the creator of this chatbot!  
I am passionate about **AI, Machine Learning, Generative AI, Data Science and Full-Stack Development**.  
This chatbot is designed to Tutor about Data Science related concepts.  
""")

# Contact Section
st.write("### 🌐Connect with Me:")
st.markdown("""
- 💼 **LinkedIn:** [Rajeswari Damam](https://www.linkedin.com/in/rajeswaridamam/)  
- ✉️ **Email:** rajeswaridamam007@gmail.com   
- 💻 **GitHub:** [Rajeswari Damam](https://github.com/damamrajeswari)
""", unsafe_allow_html=True)

# Divider Line
st.markdown("---")

st.title("🤖 About This Chatbot")

st.write("### 🔥 About This Chatbot:")
st.write("""
             This chatbot is built using **Streamlit, LangChain, and Google Gemini API**.  
         It supports **multi-session chat history, user authentication, and intelligent responses**.
         """)

st.write("### 🚀 Key Features:")
features = [
    "🔹 **AI-Powered Responses** - Uses Google Gemini for intelligent and context-aware replies.",
    "🔹 **Multi-Session Chat History** - Saves and retrieves past conversations for better continuity.",
    "🔹 **User Authentication** - Secure login system with chat history linked to user accounts.",        
    "🔹 **Customizable System Prompt** - Define how the AI should behave and respond.",
    "🔹 **Modern UI with Streamlit** - Interactive and user-friendly interface.",
    "🔹 **Database-Powered Storage** - Saves chat history using SQLite/PostgreSQL."
    ]
for feature in features:
    st.write(feature)
if st.button("Check out"):
        st.switch_page("pages/home.py")

# Add a little styling (Optional)
st.markdown("""
<style>
    .stTitle { color: #ff4b4b; }
</style>
""", unsafe_allow_html=True)
