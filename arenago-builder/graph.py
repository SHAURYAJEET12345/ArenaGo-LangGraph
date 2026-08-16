from langgraph.graph import StateGraph, START, END
from state import AgentState
from agents.orchestrator import orchestrator_node
from agents.firebase_agent import firebase_agent_node
from agents.flutter_agent import flutter_agent_node
from agents.web_agent import web_agent_node
from agents.qa_agent import qa_agent_node
from tools.file_writer import file_writer_node


def route_from_orchestrator(state: AgentState) -> str:
    """
    Conditional router: reads state['next_agent'] and returns
    the next node name for LangGraph to route to.
    """
    return state.get("next_agent", "end")


def build_graph():
    workflow = StateGraph(AgentState)

    # ── Add all nodes ─────────────────────────────────────
    workflow.add_node("orchestrator",   orchestrator_node)
    workflow.add_node("firebase_agent", firebase_agent_node)
    workflow.add_node("flutter_agent",  flutter_agent_node)
    workflow.add_node("web_agent",      web_agent_node)
    workflow.add_node("qa_agent",       qa_agent_node)
    workflow.add_node("file_writer",    file_writer_node)

    # ── Entry point ────────────────────────────────────────
    workflow.add_edge(START, "orchestrator")

    # ── Orchestrator fans out to the right agent ───────────
    workflow.add_conditional_edges(
        "orchestrator",
        route_from_orchestrator,
        {
            "firebase_agent": "firebase_agent",
            "flutter_agent":  "flutter_agent",
            "web_agent":      "web_agent",
            "qa_agent":       "qa_agent",
            "file_writer":    "file_writer",
            "end":            END,
        }
    )

    # ── All agents return to orchestrator for next task ────
    workflow.add_edge("firebase_agent", "orchestrator")
    workflow.add_edge("flutter_agent",  "orchestrator")
    workflow.add_edge("web_agent",      "orchestrator")
    workflow.add_edge("qa_agent",       "orchestrator")
    workflow.add_edge("file_writer",    "orchestrator")

    return workflow.compile()
