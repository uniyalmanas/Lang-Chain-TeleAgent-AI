# 🎯 DTDL Talent Hackathon Onsite Master Context & Problem Statements Log

**Event**: The Talent Hack by Deutsche Telekom Digital Labs Private Limited  
**Onsite Finale Dates**: 24th – 25th July 2026 (DTDL Office, Gurugram/Delhi NCR)  
**Target Roles**: AI Engineer, Senior AI Engineer, AI Full Stack Engineer  
**Hiring Pipeline**: Onsite POC -> 2 Technical Interview Rounds -> 1 HR Discussion -> Job Offer  

---

## 📌 1. The 5 Official Problem Statements (Released July 23, 2026)

### **Problem Statement 1: Autonomous AI Coding Loop**
* **Goal**: Build an autonomous AI-powered coding system that can understand software requirements, plan implementation, write code, validate changes, recover from failures, and safely iterate until completion.
* **Track Options**:
  1. Autonomous feature delivery system for a large production codebase.
  2. Configurable platform for designing and managing AI coding workflows with human oversight & deterministic validation.
* **Key Requirements**: Requirement understanding, multi-file code planner, code generator, test/validation runner, self-healing bug recovery loop, HITL approval gate.

---

### **Problem Statement 2: Voice-Controlled Computer Use Agent**
* **Goal**: Develop an AI desktop assistant that understands natural voice commands and autonomously performs multi-step tasks across desktop applications.
* **Key Requirements**: Voice input processing (WebRTC / Whisper), multi-step desktop/browser execution, outcome verification, prompt injection defense, interrupt handling, audit trail.

---

### **Problem Statement 3: AI Experiment Copilot & Decision Intelligence**
* **Goal**: Create an AI-powered experimentation assistant that helps product teams design, configure, monitor, and analyze A/B experiments.
* **Key Requirements**: Hypothesis generation, experiment configuration recommendation, anomaly/issue detection, business-friendly outcome explanations, decision recommendations (scale, continue, stop, rollback).

---

### **Problem Statement 4: Configurable Decision Automation Platform**
* **Goal**: Build a production-ready decision automation platform that evaluates configurable business rules, generates explainable decisions, and exposes REST APIs.
* **Key Requirements**: Modular rule engine, NL-to-rule converter, explainable decision audit log, REST API integration, high maintainability & transparency.

---

### **Problem Statement 5: Omnichannel Consumer AI Engine for Digital Commerce**
* **Goal**: Design an AI-powered consumer intelligence engine that personalizes shopping experiences across web and mobile channels.
* **Key Requirements**: GenAI + Agentic AI persona personalization, conversational shopping assistant, contextual next-best action, intelligent cart optimizer, omnichannel journey tracking.

---

## 🏆 2. Strategic Ranking & Recommendation

1. **Top Recommendation for AI Engineer Roles**: **PS 1 — Autonomous AI Coding Loop**
   - Live code planning, automated testing/validation execution, self-correcting retry loop, AST syntax verification, and HITL diff approval dashboard.
2. **Top Recommendation for Telecom / DTDL Domain**: **PS 5 — Omnichannel Consumer AI Engine**
   - Leverages DTDL's 18M+ subscriber context (5G plan upgrades, Broadband diagnostics, FIFA World Cup 4K pass cross-sell, cart auto-optimization).

---

## 🛠️ 3. Existing Base Architecture Ready in Workspace (`D:\Hackthon`)

- **Backend**: FastAPI + LangGraph supervisor pattern + `MemorySaver` checkpointer + Multi-LLM provider fallback (Groq Llama-3.3-70b ⚡ -> Gemini 1.5 Flash).
- **Frontend**: Interactive Dark-mode Glassmorphism dashboard with live telemetry panel, agent node logs, and HITL approval banner.
- **Reference Codebase**: 19 official LangGraph architectures available under `langgraph-official/examples/`.
- **Deployment**: `Dockerfile`, `docker-compose.yml`, and 1-click launcher (`python start_server.py`).
