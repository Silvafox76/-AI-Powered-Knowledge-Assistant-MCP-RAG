
from crewai import Crew, Process
from backend.mcp.agents import prince2_agent, itil_agent, agile_agent, ai_strategy_agent
from backend.mcp.tasks import prince2_analysis_task, itil_recommendation_task, agile_planning_task, ai_strategy_task

class CrewManager:
    def __init__(self):
        self.crews = {
            "prince2_analysis": Crew(
                agents=[prince2_agent],
                tasks=[prince2_analysis_task(prince2_agent, "")], # Pass agent and empty query for initialization
                process=Process.sequential,
                verbose=True
            ),
            "itil_recommendation": Crew(
                agents=[itil_agent],
                tasks=[itil_recommendation_task(itil_agent, "")],
                process=Process.sequential,
                verbose=True
            ),
            "agile_planning": Crew(
                agents=[agile_agent],
                tasks=[agile_planning_task(agile_agent, "")],
                process=Process.sequential,
                verbose=True
            ),
            "ai_strategy": Crew(
                agents=[ai_strategy_agent],
                tasks=[ai_strategy_task(ai_strategy_agent, "")],
                process=Process.sequential,
                verbose=True
            )
        }

    def run_crew(self, query: str, agent_type: str, task_type: str, **task_kwargs):
        if task_type not in self.crews:
            raise ValueError(f"Unknown task type: {task_type}")

        crew = self.crews[task_type]
        # Dynamically update task description with the query
        for task in crew.tasks:
            task.description = f"{task.description}\nQuery: {query}"
            task.expected_output = f"{task.expected_output}\nBased on the query: {query}"

        result = crew.kickoff()
        return result

if __name__ == "__main__":
    # Example usage (requires Ollama to be running and models pulled)
    # from langchain_community.llms import Ollama
    # os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY" # CrewAI often defaults to OpenAI
    # os.environ["OPENAI_API_BASE"] = "http://localhost:11434/v1" # For Ollama

    manager = CrewManager()
    # try:
    #     response = manager.run_crew(
    #         query="What are the 7 principles of PRINCE2?",
    #         agent_type="prince2",
    #         task_type="prince2_analysis"
    #     )
    #     print("\n\nCrew Output:")
    #     print(response)
    # except Exception as e:
    #     print(f"Error running crew: {e}")
    print("CrewManager example usage is commented out. Uncomment to test with Ollama.")


