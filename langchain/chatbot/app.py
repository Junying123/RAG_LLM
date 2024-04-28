from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import streamlit as st
import os
from dotenv import load_dotenv 

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
## LangSmith tracking
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

## Prompt Template

prompt = ChatPromptTemplate.from_messages([
    # The following.Messages
    ("system", "You are a helpful assistant to respond to user queries."),
    ("user","Question:{question}")
])

## streamlit framework

st.title("Langchain Demo with OPENAI API")
input_text = st.text_area("Enter your question here")

## openAI LLM

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
output_parser = StrOutputParser()
chain = prompt|llm|output_parser

if input_text:
    with st.spinner("Processing your request..."):
        response = chain.invoke({'question': input_text})
    st.write(response)
