import streamlit as st

from google import genai
from google.genai import types

def generate_prompt(user_input, api_key):
    prompt = f"""You are a prompt expert. Your task is writing simple text prompt for 'text to image model'.
So write a good prompt that describe what user want to draw. You can add details with your own creativity but don't out from topic.
Write only the text of prompt.
Here is user input for the image:
{user_input}"""

    client = genai.Client(api_key=api_key)
    
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite-preview-02-05",
        contents=prompt,
    )
    return response


def generate_image(prompt, api_key):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_images(
        model='imagen-3.0-generate-002',
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=3,
        )
    )
    return response

# Set up the Streamlit app
st.title("Text to Image App")

# User input for API key
api_key = st.text_input("Enter your API Key:", type="password")

if api_key:
    user_input = st.text_area("Text to analyze",None)
    if st.button("Submit", type="primary"):
        prompt_json = generate_prompt(user_input, api_key)
        prompt = prompt_json.text
        images_json = generate_image(prompt, api_key)
        st.write(prompt)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.image(images_json.generated_images[0].image.image_bytes)
        with col2:
            st.image(images_json.generated_images[1].image.image_bytes)
        with col3:
            st.image(images_json.generated_images[2].image.image_bytes)
        with col4:
            st.image(images_json.generated_images[3].image.image_bytes)