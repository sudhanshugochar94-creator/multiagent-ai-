from crewai import Task
from agents import research_agent

research_task = Task(
    description="""
    Keep the research analysis concise and under 500 words.

    User request:
    {topic}

    Scientific information:
    {pdf_text}

    Extract only information supported by the provided material.
    """,

    expected_output="""
Return only:
- Main topic: 1-2 lines
- Key findings: maximum 5 bullet points
- Conclusion: maximum 2 lines
""",

    agent=research_agent
)