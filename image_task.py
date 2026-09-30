from crewai import Task
from image_agent import image_agent
from content_task import content_task

image_task = Task(
    description="""
    Create a detailed prompt for a scientific image based on the
    research and generated social media content.

    The image should:
    - Clearly represent the main scientific topic.
    - Be visually understandable.
    - Avoid unsupported scientific claims.
    - Not add facts that are absent from the research.

    Return only the final image-generation prompt.
    """,

    expected_output="""
    One detailed image-generation prompt suitable for an image generator.
    """,

    agent=image_agent,
    context=[content_task]
)