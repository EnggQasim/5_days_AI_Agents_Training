#!/usr/bin/env python
from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import getpass
import os
from langchain_google_genai import ChatGoogleGenerativeAI
import uvicorn

# Load environment variables from the .env file
load_dotenv()

# 1. Create prompt template
system_template = "Translate the following into {language}:"
prompt_template = ChatPromptTemplate.from_messages([
    ('system', system_template),
    ('user', '{text}')
])

# 2. Create model
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=GEMINI_API_KEY)
model = llm  # llm we created in cell number 1

# 3. Create parser
parser = StrOutputParser()

# 4. Create chain
chain = prompt_template | model | parser

# 5. App definition
app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple API server using LangChain's Runnable interfaces",
)

@app.get("/llm")
async def root(lang: str, text: str):
    return chain.invoke({"text": text, "language": lang})

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)