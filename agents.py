
from crewai import Agent
from langchain_community.llms import Ollama

# Initialize LLM for agents (ensure Ollama is running and models are pulled)
# For production, consider more robust LLM integration and API keys
llm = Ollama(model="llama2")

prince2_agent = Agent(
    role="PRINCE2 Expert",
    goal="Provide in-depth analysis and guidance on PRINCE2 methodology.",
    backstory="A seasoned project manager with extensive experience in PRINCE2 projects, capable of explaining its principles, themes, and processes.",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

itil_agent = Agent(
    role="ITIL Service Management Specialist",
    goal="Offer best practices and solutions based on ITIL framework for service management.",
    backstory="An IT service management consultant with deep knowledge of ITIL processes, including service strategy, design, transition, operation, and continual service improvement.",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

agile_agent = Agent(
    role="Agile Coach and Scrum Master",
    goal="Guide on Agile methodologies, Scrum, Kanban, and adaptive planning.",
    backstory="An experienced Agile practitioner who has led numerous Scrum teams and implemented Agile transformations, focusing on flexibility, collaboration, and continuous delivery.",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

ai_strategy_agent = Agent(
    role="AI Strategy Consultant",
    goal="Advise on AI adoption, strategy, and ethical implications in business.",
    backstory="A visionary AI strategist with a strong understanding of AI technologies, their business applications, and the ethical considerations involved in AI deployment.",
    verbose=True,
    allow_delegation=False,
    llm=llm
)


