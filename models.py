from sys import stdin
from pydantic import BaseModel

def input(BaseModel):
    sourceCode:str
    language:str
    stdin:str
    stdout:str
    stderr:str
def output(BaseModel):
     sourceCode:str
     language:str
     stdin:str
     stdout:str
     stderr:str
     CorrectCode:str
     AiRemarks:str