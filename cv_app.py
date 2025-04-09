import streamlit as st
import pandas as pd
from streamlit_theme import st_theme
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.callbacks import get_openai_callback
from langchain_core.messages import HumanMessage
import base64, time, io


with st.spinner("Preparing Application", show_time=True):
    theme_json = st_theme()
    time.sleep(1)
    theme = theme_json['base']

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

if theme == "dark":
    background_image_path = "./dark_bg.png"
    header_image_path = "./Header.png"
else:
    background_image_path = "./light_bg.png"
    header_image_path = "./Header.png"

set_background_image(background_image_path)
st.title("📄 AI Recruitment App")
st.image(header_image_path)

homepage_text = '''**Revolutionize Your Hiring Process with AI-Powered CV Screening!**  

Streamline your recruitment with our **AI-Based CV Screening System**, designed to help HR teams identify top talent faster and more efficiently.  
Powered by **advanced AI and machine learning**, our system automatically analyzes resumes, evaluates qualifications, and shortlists candidates based on predefined criteria.  

✅ **Save Time & Reduce Bias** – Automate CV screening and focus on high-potential candidates.  
✅ **Smart Matching** – Ensure the best fit by aligning candidate skills with job requirements.  
✅ **Seamless Integration** – Easily connect with your existing ATS for a smooth hiring workflow.  

Empower your HR division with intelligent automation and make data-driven hiring decisions with confidence!'''

with st.container(border=True):
    st.markdown(homepage_text)

def chat(req_content, uploaded_cv):
    file_content = uploaded_cv.read()
    mime_type = uploaded_cv.type

    fix_prompt = f'''You are an Expert Recruiters. Your task is review candidate data wether It's match for job requirements or not with given candidate data provided.
Here is job requirements:
{req_content}
'''

    prompt_text = HumanMessage(
        content=[
            {"type": "text", "text": fix_prompt},
            {
                "type": "media",
                "mime_type": mime_type,
                "data": file_content
            },
        ]
    )

    class ResponseFormatter(BaseModel):
        score: int = Field(description="Give score from 0 to 100 for how much this candidate suits for AI Engineer role")
        reason: str = Field(description="Give the reason about match or not the candidate with needed role")
        desc: str = Field(description="Describe the candidate's skills and capability for needed role")

    model_with_structure = llm.with_structured_output(ResponseFormatter)

    with get_openai_callback() as cb:
        structured_response = model_with_structure.invoke([prompt_text])
        completion_tokens = cb.completion_tokens
        prompt_tokens = cb.prompt_tokens
        score = structured_response.score
        reason = structured_response.reason
        desc = structured_response.desc
        price = 16_500 * (prompt_tokens*0.1 + completion_tokens*0.4)/1_000_000

    response = {
        "score" : score,
        "reason" : reason,
        "desc" : desc,
        "completion_tokens" : completion_tokens,
        "prompt_tokens" : prompt_tokens,
        "price_idr" : price
    }
    return response

api_key = st.text_input("Enter your API Key:", type="password")

if api_key:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        api_key=api_key
    )


uploaded_req = st.file_uploader(
    "**Drop Job Requirements Here**", type="txt", accept_multiple_files=False
)

if uploaded_req:
    req_content = uploaded_req.read().decode("utf-8")
    with st.expander("Job Requirements Detail"):
        st.markdown(req_content)
    
    uploaded_cvs = st.file_uploader(
        "**Upload PDF CV**", type="pdf", accept_multiple_files=True
    )

    if uploaded_cvs:
        if st.button("Analyze"):
            st.write("Candidate Analysis Results:")

            result_list = []
            for uploaded_cv in uploaded_cvs:
                st.subheader(f"📘 {uploaded_cv.name}")
                result = chat(req_content, uploaded_cv)
                result['filename'] = uploaded_cv.name
                result_list.append(result)
                st.write(result)
            
            data = pd.DataFrame(
                result_list, columns=["score", "reason", "desc", "completion_tokens", "prompt_tokens", "price_idr", "filename"]
            )            

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                data.to_excel(writer, index=False, sheet_name="Sheet1")
                writer.close()

            excel_data = output.getvalue()

            st.download_button(
                label="Download Excel",
                data=excel_data,
                file_name="data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )