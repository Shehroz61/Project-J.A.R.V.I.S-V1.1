import streamlit as st
from google import genai
import os
import logging
import hashlib
from datetime import datetime
import json

# Configure logging for server-side error tracking
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Page config - must be first Streamlit command
st.set_page_config(
    page_title="J.A.R.V.I.S Ultimate",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "J.A.R.V.I.S Ultimate v2.0 - Advanced AI Assistant"
    }
)

# Custom CSS for ultra-modern UI
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #00d4ff;
        --secondary-color: #7b2cbf;
        --accent-color: #ff006e;
        --bg-dark: #0a0e17;
        --bg-card: #111827;
        --text-primary: #ffffff;
        --text-secondary: #9ca3af;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
    }
    
    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, #0a0e17 0%, #1a1a2e 50%, #16213e 100%);
        color: var(--text-primary);
    }
    
    /* Hide default header */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Chat message styling */
    .stChatMessage {
        background: rgba(17, 24, 39, 0.8);
        border-radius: 16px;
        border: 1px solid rgba(0, 212, 255, 0.1);
        backdrop-filter: blur(10px);
        margin-bottom: 16px;
        padding: 16px;
        transition: all 0.3s ease;
    }
    
    .stChatMessage:hover {
        border-color: rgba(0, 212, 255, 0.3);
        box-shadow: 0 4px 20px rgba(0, 212, 255, 0.1);
    }
    
    /* User message styling */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(123, 44, 191, 0.1) 100%);
        border-left: 3px solid var(--primary-color);
    }
    
    /* Assistant message styling */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        background: linear-gradient(135deg, rgba(123, 44, 191, 0.1) 0%, rgba(255, 0, 110, 0.1) 100%);
        border-left: 3px solid var(--secondary-color);
    }
    
    /* Input field styling */
    .stChatInput {
        background: rgba(17, 24, 39, 0.9);
        border: 2px solid rgba(0, 212, 255, 0.2);
        border-radius: 12px;
        color: white;
    }
    
    .stChatInput:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(0, 212, 255, 0.5);
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(17, 24, 39, 0.95) 0%, rgba(26, 26, 46, 0.95) 100%);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(0, 212, 255, 0.1);
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(17, 24, 39, 0.8) 0%, rgba(26, 26, 46, 0.8) 100%);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(0, 212, 255, 0.1);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: var(--primary-color);
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 212, 255, 0.15);
    }
    
    /* Title styling */
    h1, h2, h3 {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 50%, var(--accent-color) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
    }
    
    /* Info boxes */
    .stInfo {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid var(--success-color);
        border-radius: 8px;
        padding: 12px 16px;
    }
    
    /* Warning boxes */
    .stWarning {
        background: rgba(245, 158, 11, 0.1);
        border-left: 4px solid var(--warning-color);
        border-radius: 8px;
        padding: 12px 16px;
    }
    
    /* Error boxes */
    .stError {
        background: rgba(239, 68, 68, 0.1);
        border-left: 4px solid var(--error-color);
        border-radius: 8px;
        padding: 12px 16px;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(17, 24, 39, 0.5);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-color);
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-top-color: var(--primary-color);
    }
    
    /* Markdown content */
    .stMarkdown {
        color: var(--text-primary);
        line-height: 1.6;
    }
    
    /* Code blocks */
    pre {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 8px;
        padding: 16px;
        border: 1px solid rgba(0, 212, 255, 0.1);
    }
    
    /* Divider */
    hr {
        border-color: rgba(0, 212, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Get API key from Streamlit secrets, falling back to environment variable
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    # Fallback to environment variable if not in Streamlit secrets
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("🔑 Google API Key not found! Please set it in Streamlit secrets or as an environment variable.")
    st.stop()

# Get model name from environment variable with default fallback
MODEL_NAME = os.getenv("GOOGLE_MODEL_NAME", "gemini-2.5-flash")

# Maximum input length to prevent abuse
MAX_INPUT_LENGTH = 4000

# Cache TTL for responses (in seconds)
CACHE_TTL = 3600  # 1 hour

@st.cache_resource
def get_client():
    """Initialize and cache the Google AI client."""
    return genai.Client(api_key=GOOGLE_API_KEY)

client = get_client()

@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def get_ai_response(prompt_hash, full_prompt, model_name):
    """Cache AI responses to avoid redundant API calls for identical queries."""
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=full_prompt
        )
        return response.text, None
    except Exception as e:
        logger.error(f"AI request failed: {str(e)}", exc_info=True)
        return None, str(e)

# Define different AI roles with their behaviors
roles = {
    "🤖 General Assistant": "You are a helpful assistant. Answer questions clearly and concisely.",
    "💼 Sales Representative": "You are a friendly and persuasive sales representative. Focus on benefits, features, and closing deals. Be enthusiastic and helpful.",
    "🎧 Customer Support": "You are a patient and empathetic customer support agent. Listen carefully to problems and provide step-by-step solutions.",
    "📊 Business Advisor": "You are a professional business advisor. Provide strategic insights, data-driven recommendations, and industry expertise.",
    "⚙️ Technical Expert": "You are a technical expert. Provide detailed, accurate technical information with examples and best practices.",
    "✍️ Creative Writer": "You are a creative writer. Respond with imagination, vivid descriptions, and engaging storytelling.",
    "🎯 Marketing Specialist": "You are a marketing specialist. Provide creative marketing strategies, campaign ideas, and brand positioning advice.",
    "📱 Social Media Manager": "You are a social media expert. Create engaging content, suggest posting strategies, and help build online presence.",
    "🔬 Research Analyst": "You are a research analyst. Provide well-researched, evidence-based information with citations when possible.",
    "🎨 Design Consultant": "You are a design consultant. Offer creative design advice, UX/UI best practices, and visual aesthetics guidance."
}

# Temperature settings
temperature_options = {
    "🎯 Precise (0.2)": 0.2,
    "⚖️ Balanced (0.5)": 0.5,
    "🎨 Creative (0.8)": 0.8,
    "🔥 Very Creative (1.0)": 1.0
}

# Pre-compute role instructions
ROLE_INSTRUCTIONS = {k: v for k, v in roles.items()}

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = datetime.now()
if "tokens_used" not in st.session_state:
    st.session_state.tokens_used = 0

# Header with animated gradient
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.title("🤖 J.A.R.V.I.S Ultimate v2.0")
    st.markdown("<p style='text-align: center; color: #9ca3af; font-size: 14px;'>Advanced AI Assistant System</p>", unsafe_allow_html=True)

# Sidebar with advanced controls
with st.sidebar:
    # Developer info with modern card
    st.markdown("""
    <div class="metric-card" style="text-align: center; margin-bottom: 20px;">
        <h3 style="margin: 0; font-size: 18px;">💻 Developed By</h3>
        <p style="margin: 8px 0; color: var(--primary-color); font-weight: 600;">Shehroz Hameed & Chaury Saab</p>
        <p style="margin: 4px 0; font-size: 12px; color: var(--text-secondary);">J.A.R.V.I.S Ultimate Edition</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Role selection with enhanced UI
    st.subheader("🎭 AI Persona")
    selected_role = st.selectbox(
        "Choose AI Role:",
        list(roles.keys()),
        label_visibility="collapsed"
    )
    role_instruction = roles[selected_role]
    
    # Temperature control
    st.subheader("🌡️ Creativity Level")
    selected_temp = st.select_slider(
        "Response Temperature:",
        options=list(temperature_options.keys()),
        value="⚖️ Balanced (0.5)",
        label_visibility="collapsed"
    )
    temperature = temperature_options[selected_temp]
    
    # Show current configuration
    st.divider()
    st.subheader("⚙️ Current Configuration")
    st.info(f"**Role:** {selected_role}")
    st.info(f"**Temperature:** {temperature}")
    st.info(f"**Model:** {MODEL_NAME}")
    
    st.divider()
    
    # Statistics dashboard
    st.subheader("📊 Session Statistics")
    
    # Calculate session duration
    session_duration = datetime.now() - st.session_state.start_time
    hours, remainder = divmod(int(session_duration.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.metric(
            label="Messages",
            value=len(st.session_state.messages),
            delta=None
        )
    with col_stat2:
        st.metric(
            label="Session Time",
            value=f"{hours:02d}:{minutes:02d}:{seconds:02d}",
            delta=None
        )
    
    st.divider()
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    
    col_clear1, col_clear2 = st.columns(2)
    with col_clear1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_count = 0
            st.rerun()
    
    with col_clear2:
        if st.button("💾 Export Chat", use_container_width=True):
            chat_json = json.dumps(st.session_state.messages, indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=chat_json,
                file_name=f"jarvis_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    st.divider()
    
    # Feature highlights
    st.subheader("✨ Features")
    st.markdown("""
    - 🎭 10+ AI Personas
    - 🌡️ Adjustable Creativity
    - 💾 Export Conversations
    - ⚡ Response Caching
    - 🔒 Secure API Handling
    - 📊 Real-time Stats
    - 🎨 Ultra-Modern UI
    """)

# Main chat area
# Display chat history with enhanced styling
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])
        if "timestamp" in message:
            st.caption(f"🕐 {message['timestamp']}")

# Enhanced chat input
st.divider()
prompt_placeholder = "💬 Ask me anything... (Press Enter to send)"

# Get user input with enhanced validation
if prompt := st.chat_input(prompt_placeholder):
    # Validate input length
    if len(prompt) > MAX_INPUT_LENGTH:
        st.error(f"⚠️ Input too long! Maximum length is {MAX_INPUT_LENGTH} characters. Your input: {len(prompt)} characters.")
        st.stop()
    
    if not prompt.strip():
        st.warning("⚠️ Please enter a message.")
        st.stop()
    
    # Increment chat count
    st.session_state.chat_count += 1
    
    # Show user message with timestamp
    user_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.chat_message("user", avatar="👤").markdown(prompt)
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "timestamp": user_timestamp
    })

    # Enhanced loading indicator
    with st.spinner("🧠 J.A.R.V.I.S is thinking..."):
        # Sanitize input to prevent prompt injection attempts
        sanitized_prompt = prompt.replace("Ignore previous instructions", "")\
                                      .replace("System:", "")\
                                      .replace("You are now", "")\
                                      .replace("Override:", "")\
                                      .replace("Bypass:", "")\
                                      .replace("Skip instructions:", "")
        
        # Combine role instruction with user prompt
        full_prompt = f"{role_instruction}\n\nTemperature: {temperature}\n\nUser Query: {sanitized_prompt}"
        
        # Create a hash of the prompt for cache key
        prompt_hash = hashlib.md5(full_prompt.encode()).hexdigest()

        # Get AI response (with caching)
        response_text, error = get_ai_response(prompt_hash, full_prompt, MODEL_NAME)
        
        if error:
            response_text = f"""❌ **An error occurred while processing your request.**

**Error Details:**
```
{error}
```

**Suggestions:**
- Check your internet connection
- Verify your API key is valid
- Try rephrasing your question
- Contact support if the issue persists

*Please try again later.*"""

    # Show assistant response with timestamp
    assistant_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(response_text)
        st.caption(f"🕐 {assistant_timestamp} | 🌡️ Temp: {temperature}")

    # Save assistant response with metadata
    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text,
        "timestamp": assistant_timestamp,
        "temperature": temperature,
        "role_used": selected_role
    })

# Footer with status indicator
st.divider()
col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
with col_f2:
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <p style="color: var(--text-secondary); font-size: 12px;">
            🟢 System Online | Powered by Google AI | Response Caching Enabled
        </p>
        <p style="color: var(--text-secondary); font-size: 10px;">
            J.A.R.V.I.S Ultimate v2.0 © 2024
        </p>
    </div>
    """, unsafe_allow_html=True)
