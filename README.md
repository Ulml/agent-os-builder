# Agent OS Builder

Système multi-agents avec LangGraph, auto-génération d'agents, persistance, feedbacks en cascade (Juge → Humain → Peer), et interface chatbot + Kanban.

## Installation

```bash
cd agent-os-builder
pip install -r requirements.txt
cp .env.example .env
# Édite .env avec tes clés API
streamlit run app.py
```

## Fonctionnalités
- Auto-génération dynamique d'agents avec LangGraph
- Persistance des agents et feedbacks
- Feedback en cascade : Agent Juge → Humain → Peer
- Support multi-LLM : Anthropic (Claude), Google Gemini, xAI Grok
- Interface Streamlit avec onglet Settings pour clés API

