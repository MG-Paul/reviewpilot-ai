from typing import TypedDict, Dict, Any, List
from langgraph.graph import StateGraph, END
from app.core.config import settings

class ScreeningState(TypedDict):
    title: str
    abstract: str
    picos: Dict[str, Any]
    decision: str # include, exclude, maybe
    reason_code: str # wrong_population, wrong_intervention, etc.
    explanation: str

async def evaluate_population(state: ScreeningState) -> Dict[str, Any]:
    """Node checking population inclusion."""
    title_abs = (state["title"] + " " + state["abstract"]).lower()
    picos = state["picos"] or {}
    population_terms = picos.get("population", [])
    
    # Heuristic fallback if terms listed
    if population_terms:
        matched = any(term.lower() in title_abs for term in population_terms)
        if not matched:
            return {
                "decision": "exclude",
                "reason_code": "wrong_population",
                "explanation": f"Study does not mention target population terms: {', '.join(population_terms)}"
            }
    return {"decision": "continue"}

async def evaluate_intervention(state: ScreeningState) -> Dict[str, Any]:
    """Node checking intervention inclusion."""
    title_abs = (state["title"] + " " + state["abstract"]).lower()
    picos = state["picos"] or {}
    intervention_terms = picos.get("intervention", [])
    
    if intervention_terms:
        matched = any(term.lower() in title_abs for term in intervention_terms)
        if not matched:
            return {
                "decision": "exclude",
                "reason_code": "wrong_intervention",
                "explanation": f"Study does not mention target intervention terms: {', '.join(intervention_terms)}"
            }
    return {"decision": "include", "reason_code": "eligible", "explanation": "Study matches population and intervention screening criteria."}

# Routing function
def route_screening(state: ScreeningState):
    if state.get("decision") == "exclude":
        return END
    return "check_intervention"

# Build LangGraph StateGraph
builder = StateGraph(ScreeningState)
builder.add_node("check_population", evaluate_population)
builder.add_node("check_intervention", evaluate_intervention)

builder.set_entry_point("check_population")
builder.add_conditional_edges(
    "check_population",
    route_screening,
    {
        END: END,
        "check_intervention": "check_intervention"
    }
)
builder.add_edge("check_intervention", END)

screening_graph = builder.compile()

async def run_ai_screening(title: str, abstract: str, picos: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes the compiled screening workflow graph.
    """
    initial_state = {
        "title": title,
        "abstract": abstract,
        "picos": picos,
        "decision": "continue",
        "reason_code": "",
        "explanation": ""
    }
    
    # Run through graph nodes
    result = await screening_graph.ainvoke(initial_state)
    return {
        "decision": result["decision"],
        "reason_code": result["reason_code"],
        "explanation": result["explanation"]
    }
