from pydantic import BaseModel, Field
from typing import Optional


class CodeInput(BaseModel):
    """Input model for the AI code checker endpoint."""
    source_code: str = Field(..., description="The source code to analyze")
    language: str = Field(..., description="Programming language (e.g. python, javascript, cpp)")
    stdin: Optional[str] = Field(default="", description="Standard input provided to the program")
    stdout: Optional[str] = Field(default="", description="Actual standard output from execution")
    stderr: Optional[str] = Field(default="", description="Standard error output from execution")


class CodeOutput(BaseModel):
    """Output model returned by the AI code checker endpoint."""
    source_code: str = Field(..., description="The original source code submitted")
    language: str = Field(..., description="Programming language of the code")
    stdin: str = Field(default="", description="Standard input that was provided")
    stdout: str = Field(default="", description="Standard output from execution")
    stderr: str = Field(default="", description="Standard error from execution")
    corrected_code: str = Field(default="", description="AI-corrected version of the code")
    has_errors: bool = Field(default=False, description="Whether the code had errors")
    ai_remarks: str = Field(default="", description="AI analysis remarks and explanation")
    improvements: str = Field(default="", description="Suggested improvements for the code")