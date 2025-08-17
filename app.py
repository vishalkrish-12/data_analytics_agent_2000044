import json
import re
from fastapi import FastAPI, Request
import tempfile
from agents import get_agent
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_json_array(text):
    """
    Extracts the first JSON array from a string, even if it's inside a markdown code block or a dict.
    """
    # If already a list, return as is
    if isinstance(text, list):
        return text
    # If already a dict with 'output', extract
    if isinstance(text, dict):
        if "output" in text:
            return text["output"]
        return [text]
    # Otherwise, treat as string
    if not isinstance(text, str):
        text = str(text)
    # Remove markdown code block if present
    text = re.sub(r"^```json|^```python|^```", "", text, flags=re.MULTILINE).strip()
    text = re.sub(r"```$", "", text, flags=re.MULTILINE).strip()
    # Try to find the first JSON array in the text
    match = re.search(r"\[\s*[\s\S]*?\]", text)
    if match:
        return json.loads(match.group(0))
    # If it's a dict with 'output', extract that
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict) and "output" in parsed:
            return parsed["output"]
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass
    # Fallback: return the raw text as a single-element list
    return [text]

@app.post("/api/")
async def analyze_endpoint(request: Request):
    form = await request.form()
    question_file = form.get("questions.txt")
    if question_file is None:
        return ["Error: questions.txt required."]
    question_str = question_file.file.read().decode("utf-8")
    prompt = question_str.strip()
    attachments = {}

    # Save files (except questions.txt) to temp, so they can be referenced by agent/tools
    for key in form.keys():
        if key == "questions.txt":
            continue
        file_obj = form.get(key)
        if hasattr(file_obj, 'filename'):
            suffix = "." + file_obj.filename.split('.')[-1] if '.' in file_obj.filename else ''
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(file_obj.file.read())
                attachments[file_obj.filename] = tmp.name

    agent = get_agent()

    # --- NEW: Make the agent aware of uploaded files ---
    uploaded_files = [fname for fname in attachments.keys()]
    if uploaded_files:
        files_info = (
            "The following files are available for your analysis: "
            + ", ".join(uploaded_files) + ".\n"
            "Use the file 'irs.csv' as the dataset for your analysis if referenced in the question.\n"
        )
    else:
        files_info = ""
    # ---------------------------------------------------

    # Strict prompt for array-only output
    context = (
        f"{prompt}\n"
        f"{files_info}"
        "You are an autonomous data analytics agent. You will receive a question.txt file containing a paragraph describing an analytics scenario, followed by one or more numbered questions (e.g., 1), 2), etc.).\n"
        "Your tasks are:\n"
        "- Carefully read and understand the scenario description and the numbered questions.\n"
        "- Identify and count the number of analytics questions being asked.\n"
        "- For each question:\n"
        "    - Break down the task into logical subtasks.\n"
        "    - Determine which tools to use for each subtask (WebScraperTool, Python tool, VisionTool).\n"
        "    - Chain tool outputs as needed (e.g., use the output of WebScraperTool as input to the Python tool).\n"
        "    - If a web URL is provided, use WebScraperTool to extract the relevant table as CSV.\n"
        "    - Load CSV text into a pandas DataFrame using the Python tool. Do NOT try to read from a file unless you have saved the CSV to disk.\n"
        "    - Perform all further analysis and plotting in Python using the DataFrame.\n"
        "    - When generating Python code, use multi-line code blocks (not a single line with semicolons) for loops, with-statements, and control structures.\n"
        "    - For plotting, return the plot as a base64 data URI string under 100,000 bytes.\n"
        "    - If you encounter an error, attempt to rectify it and continue. If unresolved, explain the error in your answer.\n"
        "- Return the final output as a JSON array, with one answer per question, in the order the questions were asked. The length of the array must match the number of questions.\n"
        "- For numeric answers, return as numbers or arrays. For plots, return only the base64 data URI string.\n"
        "- Do NOT include the prompt, instructions, or any explanation in your response. Do NOT wrap the answers in an object or dictionary. Do NOT use markdown code blocks. Only return the JSON array.\n"
        "Be methodical, robust, and concise. Always ensure your output matches the required format.\n"
    )
    answer = agent.invoke(context)

    # Extract the JSON array from the agent's output
    results = extract_json_array(answer)

    # Count number of questions (lines starting with 1), 2), etc.)
    num_questions = sum(
        1 for line in prompt.splitlines()
        if line.strip().startswith(tuple(f"{i})" for i in range(1, 21)))
    )
    while len(results) < num_questions:
        results.append("")

    return results