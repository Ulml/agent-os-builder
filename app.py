import streamlit as st
from dotenv import load_dotenv, dotenv_values
from core.graph import graph
from core.persistence import get_recent_agents, get_feedback_counts
import os

load_dotenv()


def _env_value(name: str) -> str:
    file_values = dotenv_values(".env")
    return (file_values.get(name) or os.getenv(name) or "").strip()

st.set_page_config(page_title="Agent OS Builder", layout="wide")
st.title("🧠 Agent OS Builder - Version Complète")

tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat Orchestrateur", "📋 Kanban", "🔧 Paramètres", "🕸️ Graph LangGraph"])

with tab3:
    st.header("Clés API")
    anthropic = st.text_input("Anthropic (Claude)", value=_env_value("ANTHROPIC_API_KEY"), type="password")
    gemini = st.text_input("Gemini", value=_env_value("GEMINI_API_KEY"), type="password")
    grok = st.text_input("Grok", value=_env_value("GROK_API_KEY"), type="password")
    if st.button("💾 Sauvegarder clés"):
        with open(".env", "w", encoding="utf-8") as f:
            f.write(f"ANTHROPIC_API_KEY={anthropic}\n")
            f.write(f"GEMINI_API_KEY={gemini}\n")
            f.write(f"GROK_API_KEY={grok}\n")

        # Update current process env to avoid mandatory restart for this session.
        os.environ["ANTHROPIC_API_KEY"] = anthropic
        os.environ["GEMINI_API_KEY"] = gemini
        os.environ["GROK_API_KEY"] = grok

        st.success("Clés sauvegardées et chargées dans la session courante.")

with tab1:
    st.header("Chat avec l'Orchestrateur")
    st.caption("Le système crée des agents + boucle de feedback (Juge → Humain → Peer)")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Quelle est ta demande ?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Création du réseau d'agents + boucle de révision..."):
                try:
                    result = graph.invoke({"task": prompt})
                    response = f"""**✅ Réseau d'agents créé !**

Agent principal : {result.get('current_agent', 'N/A')}
Étape : {result.get('stage', 'unknown')}

**Résultat :** {result.get('output', 'Traitement terminé')}"""
                except Exception as e:
                    response = f"Erreur : {str(e)}"
                
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

with tab2:
    st.header("📋 Kanban - Avancement")
    st.info("Système de suivi des tâches en développement (v2).")

with tab4:
    st.header("Graph des agents créés")
    st.caption("Vue dynamique basée sur les agents et feedbacks stockés en base.")

    agents = get_recent_agents(limit=25)
    if not agents:
        st.info("Aucun agent créé pour le moment. Envoie une demande dans l'onglet Chat.")
    else:
        dot_lines = [
            "digraph AgentGraph {",
            "  rankdir=LR;",
            '  node [shape=box, style="rounded,filled", fillcolor="#f6f8ff", color="#6573c3"];',
            '  request [label="Dernières demandes", shape=oval, fillcolor="#eef2ff"];',
        ]

        for idx, agent in enumerate(agents):
            node_id = f"a{idx}"
            label = (agent["name"] or agent["agent_id"]).replace('"', "")
            counts = get_feedback_counts(agent["agent_id"])
            dot_lines.append(
                f'  {node_id} [label="{label}\\n{agent["agent_id"]}", fillcolor="#ffffff"];'
            )
            dot_lines.append(f"  request -> {node_id} [label=\"create\"];")

            if counts.get("judge", 0) > 0:
                judge_id = f"{node_id}_judge"
                dot_lines.append(
                    f'  {judge_id} [label="Judge x{counts["judge"]}", shape=ellipse, fillcolor="#fff7e6", color="#d48806"];'
                )
                dot_lines.append(f"  {node_id} -> {judge_id};")

            if counts.get("human", 0) > 0:
                human_id = f"{node_id}_human"
                dot_lines.append(
                    f'  {human_id} [label="Human x{counts["human"]}", shape=ellipse, fillcolor="#f6ffed", color="#389e0d"];'
                )
                dot_lines.append(f"  {node_id} -> {human_id};")

            if counts.get("peer", 0) > 0:
                peer_id = f"{node_id}_peer"
                dot_lines.append(
                    f'  {peer_id} [label="Peer x{counts["peer"]}", shape=ellipse, fillcolor="#fff0f6", color="#c41d7f"];'
                )
                dot_lines.append(f"  {node_id} -> {peer_id};")

        dot_lines.append("}")
        st.graphviz_chart("\n".join(dot_lines), use_container_width=True)

        with st.expander("Voir le workflow LangGraph statique"):
            st.caption("Structure du pipeline compilé (START → factory → judge → peer → END).")
            try:
                mermaid_text = graph.get_graph().draw_mermaid()
                st.code(mermaid_text, language="mermaid")
            except Exception as e:
                st.error(f"Impossible d'afficher le workflow statique: {e}")

st.caption("Version complète basée sur notre conversation - LangGraph + Persistance + Feedbacks")