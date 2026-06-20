import os
import json
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

from models import CodeInput, CodeOutput

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("runbox-ai")

app = FastAPI(
    title="RunBox AI",
    description="AI-powered code analysis, error detection, and improvement suggestions.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are an expert code reviewer and debugger. You will receive:
- source_code: the user's code
- language: the programming language
- stdin: the standard input fed to the program (may be empty)
- stdout: the actual standard output produced (may be empty)
- stderr: the standard error output produced (may be empty)

Your job:
1. **Analyze** the code for syntax errors, runtime errors, logical bugs, and edge-case failures.
2. **Cross-check** stderr/stdout against expected behaviour.
3. **Fix** every issue you find and produce a corrected version of the code.
4. **Remark** on what was wrong, why, and how your fix addresses it.
5. **Suggest improvements** (performance, readability, best practices, security).

You MUST reply with **valid JSON only** (no markdown fences, no extra text) using exactly these keys:
{
  "corrected_code": "<the full corrected source code>",
  "has_errors": true | false,
  "ai_remarks": "<detailed explanation of issues found and fixes applied>",
  "improvements": "<suggested improvements beyond the bug fixes>"
}
"""


def _build_user_prompt(data: CodeInput) -> str:
    return (
        f"### Language\n{data.language}\n\n"
        f"### Source Code\n```\n{data.source_code}\n```\n\n"
        f"### Standard Input (stdin)\n```\n{data.stdin}\n```\n\n"
        f"### Standard Output (stdout)\n```\n{data.stdout}\n```\n\n"
        f"### Standard Error (stderr)\n```\n{data.stderr}\n```"
    )


@app.get("/")
def health_check():
    return {"status": "ok", "service": "RunBox AI"}


@app.post("/aicheck", response_model=CodeOutput)
def ai_checker(payload: CodeInput):
    logger.info(
        "AI check requested – language=%s, code_length=%d",
        payload.language,
        len(payload.source_code),
    )

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_prompt(payload)},
            ],
        )
    except OpenAIError as exc:
        logger.error("OpenAI API error: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=f"Upstream AI service error: {exc}",
        )

    raw_content: str = completion.choices[0].message.content or ""
    logger.info("Raw AI response (first 300 chars): %s", raw_content[:300])

    try:
        ai_result = json.loads(raw_content)
    except json.JSONDecodeError:
        logger.error("AI returned non-JSON: %s", raw_content[:500])
        raise HTTPException(
            status_code=502,
            detail="AI returned an unparsable response. Please retry.",
        )

    return CodeOutput(
        source_code=payload.source_code,
        language=payload.language,
        stdin=payload.stdin or "",
        stdout=payload.stdout or "",
        stderr=payload.stderr or "",
        corrected_code=ai_result.get("corrected_code", payload.source_code),
        has_errors=ai_result.get("has_errors", False),
        ai_remarks=ai_result.get("ai_remarks", "No remarks."),
        improvements=ai_result.get("improvements", "No suggestions."),
    )