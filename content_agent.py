from crewai import Agent
from agents import groq_llm

content_agent = Agent(
    role="Scientific Content Creator",
    goal="Create accurate and engaging X/Twitter content from the research analysis.",
    backstory=(
        "You are a scientific social media content creator. "
        "You convert research findings into clear social media content "
        "without inventing scientific facts."
    ),
    llm=groq_llm,
    verbose=True
)