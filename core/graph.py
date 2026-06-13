from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from core.llm import get_llm
from core.persistence import save_agent, get_feedbacks
import json


class AgentState(TypedDict):
    task: str
    messages: list
    current_agent: str
    output: str


def agent_factory(state):
    llm = get_llm()
    prompt = f"""Crée un agent spécialisé pour cette tâche : {state['task']}
Retourne uniquement du JSON : {{"name": "...", "role": "...", "goal": "...", "backstory": "..."}}"""

    response = llm.invoke(prompt)
    try:
        data = json.loads(response.content)
        agent_id = data["name"].replace(" ", "_").lower()
        system_prompt = f"""Tu es {data['name']}. Rôle : {data['role']}. Objectif : {data['goal']}.
{data.get('backstory', '')}

Feedbacks précédents : {get_feedbacks(agent_id)}"""

        save_agent(agent_id, data["name"], system_prompt)
        return {"current_agent": agent_id, "output": f"Agent {data['name']} créé."}
    except:
        return {"output": "Erreur création agent"}


# Construction du graphe
workflow = StateGraph(AgentState)
workflow.add_node("factory", agent_factory)
workflow.add_edge(START, "factory")
workflow.add_edge("factory", END)

graph = workflow.compile()
