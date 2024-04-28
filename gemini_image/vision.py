from dotenv import load_dotenv
import pathlib
import textwrap
from PIL import Image

load_dotenv()

import streamlit as st
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input,image):
    model = genai.GenerativeModel('gemini-pro-vision')
    if input!="":
       response = model.generate_content([input,image])
    else:
       response = model.generate_content(image)
    return response.text

st.set_page_config(page_title="Gemini Image", page_icon=":gemini:")

st.header("Gemini LLM Application")
input = st.text_input("Input: ",key="input")

upload = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
image = ""
if upload is not None:
    image = Image.open(upload)
    st.image(image, caption='Uploaded Image.', use_column_width=True)
    

submit = st.button("Tell me about the image")

if submit:
    response = get_gemini_response(input,image)
    st.subheader("The Response is")
    st.write(response)
