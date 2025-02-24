import streamlit as st
import base64
from openai import OpenAI

# Function to convert image to base64
def image_to_base64(image):
    image_bytes = image.getvalue()
    base64_encoded = base64.b64encode(image_bytes).decode('utf-8')
    return base64_encoded

# Streamlit app
st.title("Invoice Extractor App")


# User input for API key
api_key = st.text_input("Enter your API Key:", type="password")

# File uploader
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image
    st.image(uploaded_file, caption='Uploaded Image.', use_column_width=True)
    
    # Convert the image to base64
    base64_string = image_to_base64(uploaded_file)
    
    if api_key:
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
                        {"type": "text", "text": "Extract given image to this format: Transaction Date (format:YYYY-MM-DD), Vendor Name, Address, Total Price Transaction, Transaction Info : (Product Name, Quantity, Price per Unit, Discount)"}
                    ]}
                ]
            )
            response = completion.choices[0].message.content
            st.write(response)