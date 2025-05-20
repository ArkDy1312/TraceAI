from orchestrator.langgraph_workflow import build_trace_graph
import json

# Path to the file (adjust if necessary)
file_path = "data/traceability_sample_data.json"

# Open and parse
with open(file_path, "r") as f:
    all_workspace_data = json.load(f)

def run_trace():
    graph = build_trace_graph()
    for data in all_workspace_data:
        graph.invoke(data)
