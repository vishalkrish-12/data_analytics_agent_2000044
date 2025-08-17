from langchain_community.chat_models import ChatOpenAI
from tools.web import WebScraperTool
from tools.code import ExtendedPythonTool
from tools.vision import VisionTool
import os
from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentType

load_dotenv()  # Load environment variables from .env file
openai_api_key = os.getenv("OPENAI_API_KEY")

def get_llm():
    return ChatOpenAI(
        openai_api_key=openai_api_key,
        # model="gpt-4o-mini",  # or "gpt-4o"
        model="gpt-4.1-mini",
        temperature=0.2,
    )

def get_tools():
    return [
        WebScraperTool,
        ExtendedPythonTool(),
        VisionTool,
    ]

def get_agent():
    # Structured chat agent for multi-step reasoning and tool chaining
    return initialize_agent(
        tools=get_tools(),
        llm=get_llm(),
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
    )