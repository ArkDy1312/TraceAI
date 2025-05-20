from langgraph.graph import END, StateGraph

from agents.dev_agent import dev_agent_step
from agents.pm_agent import pm_agent_step
from agents.qa_agent import qa_agent_step
from state.trace_state import TraceState


# Build the LangGraph workflow
def build_trace_graph():
    builder = StateGraph(TraceState)

    builder.add_node("pm", pm_agent_step)
    builder.add_node("dev", dev_agent_step)
    builder.add_node("qa", qa_agent_step)

    builder.set_entry_point("pm")
    builder.add_edge("pm", "dev")
    builder.add_edge("dev", "qa")
    builder.add_edge("qa", END)

    return builder.compile()
