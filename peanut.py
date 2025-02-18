import streamlit as st
import requests
import json
import os
import threading
from streamlit_modal import Modal

# Streamlit page configuration
st.set_page_config(page_title="Peanut Chat", layout="wide")

# Sidebar title with icon
st.sidebar.image("assets/icon.png", width=50)
st.sidebar.title("Peanut Chatbot")

# Define default folders
HISTORY_FOLDER = "history"
PROMPT_FOLDER = "prompt"
os.makedirs(HISTORY_FOLDER, exist_ok=True)
os.makedirs(PROMPT_FOLDER, exist_ok=True)

# Initialize chat state
def init():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "history_loaded" not in st.session_state:
        st.session_state["history_loaded"] = False
    if "system_prompt" not in st.session_state:
        st.session_state["system_prompt"] = "You are a helpful AI assistant."
    if "temperature" not in st.session_state:
        st.session_state["temperature"] = 0.7
    if "awaiting_response" not in st.session_state:
        st.session_state["awaiting_response"] = False
    if "stop_event" not in st.session_state:
        st.session_state["stop_event"] = threading.Event()
    if "prompt_editor_open" not in st.session_state:
        st.session_state["prompt_editor_open"] = False
    if "temp_prompt" not in st.session_state:
        st.session_state["temp_prompt"] = st.session_state["system_prompt"]

# Define callback functions
def disable_input():
    st.session_state["awaiting_response"] = True
    st.session_state["stop_event"].clear()

def enable_input():
    st.session_state["awaiting_response"] = False

def toggle_prompt_editor():
    st.session_state["prompt_editor_open"] = not st.session_state["prompt_editor_open"]

# Define function to send message to Peanut API
def send_message(message, history, system_prompt, temperature):
    url = "http://localhost:30000/v1/chat/completions"
    payload = {
        "messages": [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}],
        "temperature": temperature,
        "stream": False
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=10)
    if st.session_state["stop_event"].is_set():
        return "Response stopped by user."
    
    if response.status_code == 200:
        response_data = response.json()
        if "choices" in response_data and len(response_data["choices"]) > 0:
            return response_data["choices"][0].get("message", {}).get("content", "Error: No content in response.")
    return "Error: Unable to connect to the model."


init()

import json

# Convert chat history to a readable text format
history_text = "\n\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state["messages"]])

# Add a download button for chat history as a text file
st.sidebar.download_button(
    label="Download Chat History",
    data=history_text,
    file_name="chat_history.txt",
    mime="text/plain"
)

uploaded_file = st.sidebar.file_uploader("Load Chat History", type=["txt", "json"], accept_multiple_files=False, key="file_uploader")
if uploaded_file is not None and not st.session_state["history_loaded"]:
    file_contents = uploaded_file.read().decode("utf-8")
    try:
        st.session_state["messages"] = json.loads(file_contents)
        st.session_state["history_loaded"] = True
        st.sidebar.success("Chat history loaded!")
    except json.JSONDecodeError:
        st.sidebar.error("Invalid JSON format in uploaded file.")

# Convert chat history to a readable text format

# Add a download button for chat history as a text file
st.sidebar.download_button(
    label="Download System Prompt",
    data=st.session_state["system_prompt"],
    file_name="system_prompt.txt",
    mime="text/plain"
)

# Load prompt from file and update both system_prompt and temp_prompt
uploaded_prompt_file = st.sidebar.file_uploader("Load Prompt", type=["txt"], accept_multiple_files=False, key="prompt_uploader")

if uploaded_prompt_file is not None:
    new_prompt_content = uploaded_prompt_file.read().decode("utf-8").strip()
    st.session_state["system_prompt"] = new_prompt_content
    st.session_state["temp_prompt"] = new_prompt_content  # Update temp_prompt to match loaded file
    st.sidebar.success("Prompt loaded!")

# Ensure temp_prompt is initialized correctly
if "temp_prompt" not in st.session_state:
    st.session_state["temp_prompt"] = st.session_state["system_prompt"]

# Modal logic
modal = Modal(key="Demo Key", title="Prompt Menu")
open_modal = st.sidebar.button("Edit Prompt")

if open_modal:
    st.session_state["prompt_editor_open"] = True  # Track modal state

if st.session_state["prompt_editor_open"]:
    with modal.container():
        st.session_state["temp_prompt"] = st.text_area("Edit System Prompt", st.session_state["temp_prompt"], height=150)

        col1, col2 = st.columns([2,3])
        with col1:
            if st.button("Save"):
                st.session_state["system_prompt"] = st.session_state["temp_prompt"]  # Save changes
                st.session_state["prompt_editor_open"] = False  # Close modal
                st.rerun()  # Refresh UI to apply changes
        with col2:
            if st.button("Cancle"):
                st.session_state["prompt_editor_open"] = False  # Close modal
                st.session_state["temp_prompt"] = st.session_state["system_prompt"]  # Reset to original value
                st.rerun()  # Refresh UI

# Sidebar for temperature setting
st.sidebar.header("Temperature Setting")
st.session_state["temperature"] = st.sidebar.slider("Select Temperature", min_value=0.0, max_value=1.0, value=st.session_state["temperature"], step=0.05)

# Chat message container
chat_container = st.container()
with chat_container:
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# User input
user_input = st.chat_input("Type your message here...", disabled=st.session_state["awaiting_response"], on_submit=disable_input)

if user_input:
    # Append user message to chat history
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="assets/user_icon.png"):
        st.markdown(user_input)
    
    # Send request to Peanut server
    bot_response = send_message(user_input, st.session_state["messages"], st.session_state["system_prompt"], st.session_state["temperature"])
    
    # Append bot response to chat history
    st.session_state["messages"].append({"role": "assistant", "content": bot_response})
    with st.chat_message("assistant", avatar="assets/assistant_icon.png"): 
        st.markdown(bot_response)
    
    # Re-enable user input
    enable_input()

