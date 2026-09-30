import crewai.llms.cache as crew_cache
from image_agent import image_agent
from image_task import image_task
crew_cache.mark_cache_breakpoint = lambda msg: msg

from crewai import Crew
from agents import research_agent
from tasks import research_task
from content_agent import content_agent
from content_task import content_task

research_crew = Crew(
    agents=[
        research_agent,
        content_agent
    ],
    tasks=[
        research_task,
        content_task
    ],
    verbose=True
)