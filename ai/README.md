# AI Orchestration & Agent Core

This directory contains the cognitive orchestration node for StadiumOS:

## Directory Index
- `ai-orchestrator/`: LangGraph orchestrator node executing state graphs, managing multi-agent planning loops (Crowd, Security, Medical), and executing RAG index lookup logic.

## Core Guidelines
- Implement safety guardrails (e.g., NeMo Guardrails) to prevent prompt injection and model jailbreaking.
- Ground LLM answers using local vector database searches.
- Require manual operator approval for all critical tool executions.
