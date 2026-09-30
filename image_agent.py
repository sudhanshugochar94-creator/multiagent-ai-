from crewai import Agent
from agents import groq_llm

image_agent = Agent(
    role="Scientific Image Planner",
    goal="Create a detailed image-generation prompt based only on the research content.",
    backstory=(
        "You are a scientific visual designer. "
        "You convert scientific research findings into accurate "
        "and visually understandable image descriptions."
    ),
    llm=groq_llm,
    verbose=True
)