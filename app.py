import streamlit as st
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI

# Set up the Streamlit app
st.title("Chatbot AI")

# User input for API key
api_key = st.text_input("Enter your DeepSeek API Key:", type="password")

if api_key:
    # Initialize the OpenAI LLM with the provided API key
    llm = ChatOpenAI(
        api_key=api_key,
        model="gpt-4o-mini",
        temperature=0.6)
else:
    st.warning("Please enter your API key to start the chatbot.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Let's say: Hi Accurate!"):
    messages_history = st.session_state.get("messages", [])[-10:]
    history = "\n".join([f'{msg["role"]}: {msg["content"]}' for msg in messages_history]) or " "

    # Display user message in chat message container
    with st.chat_message("Human"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "Human", "content": prompt})
    
    # Display assistant response in chat message container
    with st.chat_message("AI"):
        response = llm.invoke(prompt)
        answer = response.content
        st.markdown(answer)
    st.session_state.messages.append({"role": "AI", "content": answer})

    with st.container():
        st.write("**History Chat:**")
        st.code(history)

    st.write("**Details:**")
    inp_tkn = response.response_metadata['token_usage']["prompt_tokens"]
    out_tkn = response.response_metadata['token_usage']["completion_tokens"]
    total_tkn = response.response_metadata['token_usage']["total_tokens"]
    model_n = response.response_metadata["model_name"]
    st.code(f'input token : {inp_tkn}\noutput token : {out_tkn}\ntotal token : {total_tkn}\nmodel : {model_n}')