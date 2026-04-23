import streamlit as st
from google import genai
import os
import logging
import hashlib
from functools import lru_cache

# Configure logging for server-side error tracking
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Get API key from Streamlit secrets, falling back to environment variable
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    # Fallback to environment variable if not in Streamlit secrets
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("Google API Key not found! Please set it in Streamlit secrets or as an environment variable.")
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
    "General Assistant": "You are a helpful assistant. Answer questions clearly and concisely.",
    "Sales Representative": "You are a friendly and persuasive sales representative. Focus on benefits, features, and closing deals. Be enthusiastic and helpful.",
    "Customer Support": "You are a patient and empathetic customer support agent. Listen carefully to problems and provide step-by-step solutions.",
    "Business Advisor": "You are a professional business advisor. Provide strategic insights, data-driven recommendations, and industry expertise.",
    "Technical Expert": "You are a technical expert. Provide detailed, accurate technical information with examples and best practices.",
    "Creative Writer": "You are a creative writer. Respond with imagination, vivid descriptions, and engaging storytelling."
}

# Pre-compute role instructions as a frozen dict for faster lookup
ROLE_INSTRUCTIONS = {k: v for k, v in roles.items()}

# Add role selection in sidebar
selected_role = st.sidebar.selectbox("Choose AI Role:", list(roles.keys()))
role_instruction = roles[selected_role]

# Show current role
st.sidebar.info(f"Current Role: {selected_role}")

# Page Title
st.set_page_config(page_title="J.A.R.V.I.S", page_icon="🤖")
st.title("🤖 J.A.R.V.I.S V.1.0 DEMO")

# Watermark in Sidebar
st.sidebar.markdown("---")
st.sidebar.write("💻 Developed By Shehroz Hameed")
st.info("💻 Developed By Chaury Saab")

# Initialize chat history (keeps messages between refreshes)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show all previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input
if prompt := st.chat_input("Ask me anything..."):
    # Validate input length
    if len(prompt) > MAX_INPUT_LENGTH:
        st.error(f"Input too long! Maximum length is {MAX_INPUT_LENGTH} characters.")
        st.stop()
    
    # Show user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Show loading spinner while waiting for AI response
    with st.spinner("🤔 Thinking..."):
        # Sanitize input to prevent prompt injection attempts
        # Remove common prompt injection patterns
        sanitized_prompt = prompt.replace("Ignore previous instructions", "")\
                                      .replace("System:", "")\
                                      .replace("You are now", "")\
                                      .replace("Override:", "")
        
        # Combine role instruction with user prompt using safe formatting
        full_prompt = f"{role_instruction}\n\nUser Query: {sanitized_prompt}"
        
        # Create a hash of the prompt for cache key
        prompt_hash = hashlib.md5(full_prompt.encode()).hexdigest()

        # Get AI response (with caching)
        response_text, error = get_ai_response(prompt_hash, full_prompt, MODEL_NAME)
        
        if error:
            # Show generic error message to user (no stack trace exposure)
            response_text = "❌ An error occurred while processing your request. Please try again later."

    # Show assistant response
    with st.chat_message("assistant"):
        st.markdown(response_text)

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": response_text})
