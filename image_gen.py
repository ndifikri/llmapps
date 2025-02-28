import streamlit as st

from google import genai
from google.genai import types
import base64

def generate_prompt(user_input, api_key):
    prompt = f"""You are a prompt expert. Your task is writing simple text prompt for 'text to image model'.
So write a good prompt that describe what user want to draw. You can add details with your own creativity but don't out from topic.
Write only the text of prompt.
Here is user input for the image:
{user_input}"""

    client = genai.Client(api_key=api_key)
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    return response


def generate_image(prompt, api_key):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_images(
        model='imagen-3.0-generate-002',
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=4,
            aspect_ratio="4:3"
        )
    )
    return response

# Function to encode the local image file to Base64
def get_base64_of_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Custom CSS to set the background image
def set_background_image(image_path):
    encoded_image = get_base64_of_image(image_path)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded_image}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Set the background image using a local file path
background_image_path = "./web_bg.jpg"  # Relative path to the image
set_background_image(background_image_path)

# Set up the Streamlit app
st.title("Image Generation App")
st.image("imagen.png")

homepage_text = '''**Bring your ideas to life with our text-to-image app!**

Simply describe your vision, and our AI will turn your words into stunning images.
Perfect for artists, designers, or anyone with a creative spark, this tool makes it easy to turn your imagination into reality.
Create effortlessly and explore endless possibilities!
'''

with st.container(border=True):
    st.markdown(homepage_text)

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