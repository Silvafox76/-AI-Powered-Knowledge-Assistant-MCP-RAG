
import gradio as gr
import requests

BACKEND_URL = "http://127.0.0.1:8000" # Replace with your backend URL when deployed

def query_rag(query: str) -> str:
    try:
        response = requests.post(f"{BACKEND_URL}/query_rag", json={"query": query})
        response.raise_for_status()
        return response.json().get("response", "No response from RAG.")
    except requests.exceptions.RequestException as e:
        return f"Error querying RAG: {e}"

def run_mcp(query: str, agent_type: str, task_type: str, task_kwargs: str) -> str:
    try:
        # task_kwargs is a string, try to parse it as JSON
        try:
            parsed_task_kwargs = eval(task_kwargs) # Using eval for simplicity, but consider json.loads for production
        except Exception:
            parsed_task_kwargs = {}

        payload = {
            "query": query,
            "agent_type": agent_type,
            "task_type": task_type,
            "task_kwargs": parsed_task_kwargs
        }
        response = requests.post(f"{BACKEND_URL}/run_mcp", json=payload)
        response.raise_for_status()
        return response.json().get("response", "No response from MCP.")
    except requests.exceptions.RequestException as e:
        return f"Error running MCP: {e}"

with gr.Blocks() as demo:
    gr.Markdown("# AI-Powered Knowledge Assistant")

    with gr.Tab("RAG Query"):
        rag_query_input = gr.Textbox(label="Enter your RAG query:", placeholder="e.g., What are the key differences between PRINCE2 and MSP?")
        rag_output = gr.Textbox(label="RAG Response", interactive=False)
        rag_button = gr.Button("Get RAG Response")
        rag_button.click(query_rag, inputs=rag_query_input, outputs=rag_output)

    with gr.Tab("MCP Query"):
        mcp_query_input = gr.Textbox(label="Enter your MCP query:", placeholder="e.g., Explain the 7 principles of PRINCE2.")
        mcp_agent_type = gr.Dropdown(
            ["prince2", "itil", "agile", "ai_strategy"], label="Select Agent Type"
        )
        mcp_task_type = gr.Textbox(label="Enter Task Type:", placeholder="e.g., prince2_analysis, raci_chart, lessons_learned")
        mcp_task_kwargs = gr.Textbox(label="Task Keyword Arguments (JSON string):", placeholder="e.g., {\"project_type\": \"software development\"}")
        mcp_output = gr.Textbox(label="MCP Response", interactive=False)
        mcp_button = gr.Button("Run MCP Query")
        mcp_button.click(run_mcp, inputs=[mcp_query_input, mcp_agent_type, mcp_task_type, mcp_task_kwargs], outputs=mcp_output)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)


