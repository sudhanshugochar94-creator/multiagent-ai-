import os
from dotenv import load_dotenv
from crewai import Agent, LLM

load_dotenv()

groq_llm = LLM(
    model="groq/openai/gpt-oss-20b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.2
)

research_agent = Agent(
    role="Scientific Research Agent",
    goal="Analyze scientific research information and identify accurate, relevant facts.",
    backstory="You are a scientific research assistant who works with the provided scientific material.",
    llm=groq_llm,
    verbose=True
)