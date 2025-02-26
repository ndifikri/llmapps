import streamlit as st
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch

def get_answer(prompt, history):
    fix_prompt = f"""You are helpful assistant. Your task is answer the question from user.
User: {prompt}

Use this history conversation if you need to look at previous conversation contexts:
{history}"""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=fix_prompt
    )
    return response

def get_answer_web(prompt, history):
    fix_prompt = f"""You are helpful assistant. Your task is answer the question from user.
User: {prompt}

Use this history conversation if you need to look at previous conversation contexts:
{history}"""
    google_search_tool = Tool(
        google_search = GoogleSearch()
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=fix_prompt,
        config=GenerateContentConfig(
            tools=[google_search_tool],
            response_modalities=["TEXT"],
        )
    )
    return response

# Set up the Streamlit app
st.title("Chatbot AI")

# User input for API key
api_key = st.text_input("Enter your API Key:", type="password")

if api_key:
    client = genai.Client(api_key=api_key)
else:
    st.warning("Please enter your API key to start the chatbot.")

choose_mode = st.radio("Choose Chatbot Capability", ["default knowledge", "search on internet"])

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Let's say: Hi Celerates!"):
    messages_history = st.session_state.get("messages", [])[-10:]
    history = "\n".join([f'{msg["role"]}: {msg["content"]}' for msg in messages_history]) or " "

    # Display user message in chat message container
    with st.chat_message("Human"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "Human", "content": prompt})
    
    # Display assistant response in chat message container
    with st.chat_message("AI"):
        if choose_mode == "default knowledge":
            response = get_answer(prompt, history)
        else:
            response = get_answer_web(prompt, history)
        answer = response.text
        st.markdown(answer)
    st.session_state.messages.append({"role": "AI", "content": answer})

    with st.expander("**History Chat:**"):
        st.code(history)

    model = response.model_version
    prompt_tokens = response.usage_metadata.prompt_token_count
    completion_tokens = response.usage_metadata.candidates_token_count
    with st.expander("**Usage Details:**"):
        st.code(f'input token : {prompt_tokens}\noutput token : {completion_tokens}\nmodel : {model}')