import streamlit as st
import base64
from PIL import Image
import io
from openai import OpenAI

# Function to convert image to base64
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")  # Save image to BytesIO object
    base64_encoded = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return base64_encoded

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
            background-image: url("data:image/png;base64,{encoded_image}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Set the background image using a local file path
background_image_path = "./Background Image.png"  # Relative path to the image
set_background_image(background_image_path)

# Streamlit app
st.title("Invoice Extraction App")
st.image("Header.png")

homepage_text = '''**Simplify your invoicing process with our smart app!**

Just upload or snap a photo of your invoice, and our AI will automatically extract and organize the data into clear, well-defined fields.
Save time, reduce errors, and streamline your workflow with this effortless solution.
Perfect for businesses and individuals alike, this app makes managing invoices quicker and easier than ever.
'''

with st.container(border=True):
    st.markdown(homepage_text)

# User input for API key
api_key = st.text_input("Enter your API Key:", type="password")
base64_string = None

# Option to choose between file upload or camera capture
option = st.radio("Choose an option:", ("Upload an Image", "Capture from Camera"))

if option == "Upload an Image":
    # File uploader
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg"])
    if uploaded_file is not None:
        # Open the image using PIL
        image = Image.open(uploaded_file)
        # Display the uploaded image
        st.image(image, caption='Uploaded Image.', use_container_width=True)
        # Convert the image to base64
        base64_string = image_to_base64(image)


elif option == "Capture from Camera":
    # Camera input
    camera_image = st.camera_input("Take a picture")
    if camera_image is not None:
        # Open the image using PIL
        image = Image.open(camera_image)
        # Display the captured image
        st.image(image, caption='Captured Image.', use_container_width=True)
        # Convert the image to base64
        base64_string = image_to_base64(image)



if api_key and base64_string:
    client = OpenAI(
        # If the environment variable is not configured, replace the following line with: api_key="sk-xxx",
        api_key=api_key, 
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    )

    if st.button("Submit"):
        completion = client.chat.completions.create(
            model="qwen-vl-max", 
            messages=[
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_string}"}},
                    {"type": "text", "text": "Extract given image and write these points: Transaction Date (format:YYYY-MM-DD), Vendor Name, Address, Total Price Transaction, Transaction Info : (Product Name, Quantity, Price per Unit, Discount)"}
                ]}
            ]
        )
        response = completion.choices[0].message.content
        st.write(response)
else: pass