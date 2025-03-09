import streamlit as st
import requests
import os
from PIL import Image

# Set the title for the app
st.set_page_config(page_title="Virtual Partner Chat", page_icon="💬")

# Define folders for prompts and images
PROMPT_FOLDER = "prompts"
IMAGE_FOLDER = "images"

# Your Gemini API Key (Replace with your actual API key)
GEMINI_API_KEY = "replace"

# Define partners with corresponding image and prompt file
partners = {
    "Male Partner": {"image": "img1.jpg", "prompt_file": "softbf.txt"},
    "Female Partner": {"image": "img3.jpg", "prompt_file": "softgf.txt"},
    #"Software Partner": {"image": "software_partner.jpg", "prompt_file": "software_partner.txt"},
    #"Virtual Assistant": {"image": "virtual_assistant.jpg", "prompt_file": "virtual_assistant.txt"},
    #"Business Partner": {"image": "business_partner.jpg", "prompt_file": "business_partner.txt"},
    #"Creative Partner": {"image": "creative_partner.jpg", "prompt_file": "creative_partner.txt"}
}

# Function to load prompt from a text file
def load_prompt(filename):
    file_path = os.path.join(PROMPT_FOLDER, filename)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read().strip()
    except FileNotFoundError:
        return "Error: Prompt file not found."

# Function to get AI response using the correct Gemini API request format
def get_ai_response(partner_prompt, user_message):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": f"{partner_prompt}\nUser: {user_message}\nAI:"}]
        }]
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        response_json = response.json()
        if "candidates" in response_json and response_json["candidates"]:
            return response_json["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return "No response generated."
    else:
        return "Error: Unable to connect to AI."

# Function to display partner selection screen
def partner_selection_page():
    st.title("Choose Your Virtual Partner")

    partner_names = list(partners.keys())
    selected_partner = st.selectbox("Select a Partner", partner_names)

    partner_image = Image.open(os.path.join(IMAGE_FOLDER, partners[selected_partner]["image"]))
    st.image(partner_image, width=150, caption=selected_partner)

    if st.button("Start Chat"):
        st.session_state.selected_partner = selected_partner
        st.session_state.partner_prompt = load_prompt(partners[selected_partner]["prompt_file"])
        st.session_state.messages = []  # Initialize chat messages
        st.rerun()

# Function to display chat screen
def chat_with_partner_page():
    st.title(f"Chat with {st.session_state.selected_partner}")

    
    col1, col2 = st.columns([6, 1])


    with col2:
        partner_info = partners[st.session_state.selected_partner]
        partner_image = Image.open(os.path.join(IMAGE_FOLDER, partner_info["image"]))
        st.image(partner_image, width=150)
        st.write(f"### {st.session_state.selected_partner}")

    with col1:
        if 'messages' not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            if message["role"] == "user":
                st.write(f"**You**: {message['text']}")
            elif message["role"] == "ai":
                st.write(f"**{st.session_state.selected_partner}**: {message['text']}")

        user_message = st.text_input("Your message:")

        if st.button("Send"):
            if user_message:
                st.session_state.messages.append({"role": "user", "text": user_message})
                ai_response = get_ai_response(st.session_state.partner_prompt, user_message)
                st.session_state.messages.append({"role": "ai", "text": ai_response})
                st.rerun()

# Decide which page to show
if 'selected_partner' not in st.session_state:
    partner_selection_page()
else:
    chat_with_partner_page()
