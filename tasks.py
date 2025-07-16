
from crewai import Task

def prince2_analysis_task(agent, query):
    return Task(
        description=f"Analyze the provided query related to PRINCE2 and provide a comprehensive answer.\nQuery: {query}",
        expected_output="A detailed explanation of the PRINCE2 concept, including relevant principles, themes, or processes, in a clear and concise manner.",
        agent=agent,
    )

def itil_recommendation_task(agent, query):
    return Task(
        description=f"Provide ITIL-based recommendations or solutions for the given scenario.\nQuery: {query}",
        expected_output="Practical ITIL recommendations, referencing specific ITIL processes or functions, to address the query.",
        agent=agent,
    )

def agile_planning_task(agent, query):
    return Task(
        description=f"Develop an Agile planning strategy or explain an Agile concept based on the query.\nQuery: {query}",
        expected_output="A clear explanation of the Agile concept or a step-by-step Agile planning approach.",
        agent=agent,
    )

def ai_strategy_task(agent, query):
    return Task(
        description=f"Formulate an AI strategy or provide insights on AI adoption based on the query.\nQuery: {query}",
        expected_output="A strategic overview or detailed insights on AI, considering business implications and ethical aspects.",
        agent=agent,
    )


