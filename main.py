from fastapi import FastAPI
from dotenv import load_dotenv
import os 
from openai import OpenAI


app = FastAPI()
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/")
def getKey():
    return  os.getenv("OPENAI_API_KEY")