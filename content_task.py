from crewai import Task
from content_agent import content_agent
from tasks import research_task

content_task = Task(
    description="""
    Create an X/Twitter post using the research analysis produced by the
    Research Agent.

    User's request:
    {topic}

    Generate:
    1. A strong short hook
    2. Caption/post text
    3. Short description
    4. Relevant hashtags
    5. Scientific source/reference information if available

    Rules:
    - Use only information supported by the Research Agent's analysis.
    - Do not invent facts, numbers, results, or claims.
    - Keep the content suitable for X/Twitter.
    """,

    expected_output="""
    A structured X/Twitter content package containing:
    - Hook
    - Post/Caption
    - Description
    - Hashtags
    - References
    """,

    agent=content_agent,
    context=[research_task]
)