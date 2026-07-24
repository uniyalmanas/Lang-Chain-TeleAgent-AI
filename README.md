# 🚀 TeleAgent AI - Deutsche Telekom Digital Labs (DTDL) Master Template & POC

**TeleAgent AI** is a stateful Multi-Agent AI Customer Experience & Technical Operations platform built using **LangGraph**, **FastAPI**, **RAG Knowledge Systems**, **Human-In-The-Loop (HITL) Checkpoints**, and an **Interactive Dark-Mode Dashboard**.

It is specifically tailored to Deutsche Telekom's consumer telecom domain (Broadband diagnostics, WiFi channel optimization, Billing invoice disputes, instant credit refunds, FIFA World Cup Magenta TV passes, and 5G plan recommendations).

---

## 🏆 The Talent Hackathon Onsite Context (24th – 25th July)

* **Company**: Deutsche Telekom Digital Labs (DTDL)
* **Scale**: Serves **18M+ concurrent European subscribers** (Broadband, 5G, Billing, Magenta TV OTT streaming).
* **Onsite Challenge Format**: Develop a live Proof of Concept (POC) under real-world conditions based on a DTDL problem statement.
* **Target Roles**: AI Engineer, Senior AI Engineer, AI Full Stack Engineer.

---

## 🛠️ System Architecture

```
                                    +-----------------------+
                                    |   User Input (UI)     |
                                    +-----------+-----------+
                                                |
                                                v
                                   +-------------+-------------+
                                   |   LangGraph Supervisor    |
                                   | (Routing & Intent Classifier)|
                                   +------+------+------+------+
                                          |      |      |
                    +--------------------+      |      +--------------------+
                    |                           v                           |
        +-----------+-----------+   +-----------+-----------+   +-----------+-----------+
        | Network Agent (WiFi)  |   | Billing Agent (Refund)|   |  Plan Advisor (5G/TV) |
        +-----------+-----------+   +-----------+-----------+   +-----------+-----------+
                    |                           |                           |
                    v                           v                           v
        +-----------+-----------+   +-----------+-----------+   +-----------+-----------+
        | check_router_diag     |   | fetch_billing_statement|   | search_plan_catalog   |
        | reboot_router         |   | apply_bill_credit     |   | retrieve_kb_articles  |
        | retrieve_kb_articles  |   | (HITL Approval Step)  |   +-----------------------+
        +-----------------------+   +-----------------------+
```

---

## 📂 Official LangGraph Reference Architectures

Your workspace includes the complete official LangGraph codebase and **19 reference architectures** located at:
📁 **`langgraph-official/examples/`**

| Reference Folder | Architecture Pattern | Use Case |
| :--- | :--- | :--- |
| `customer-support` | Multi-agent customer support graphs | Ticket routing, escalations, user memory |
| `multi_agent` | Hierarchical supervisor + sub-agents | Multi-agent collaboration & delegation |
| `human_in_the_loop` | Interruption & approval nodes | Sensitive tool calls & human verification |
| `rag` | Adaptive / Self / Corrective RAG | Document & knowledge base querying |
| `plan-and-execute` | Planner + Executor loops | Complex multi-step reasoning tasks |
| `reflection` & `reflexion` | Agent self-critique | Output verification & prompt iteration |
| `chatbots` | Stateful memory checkpointers | Persistent user sessions (`MemorySaver`) |
| `code_assistant` | Tool calling & sandboxed execution | Dynamic code generation & debugging |

---

## ⚡ 60-Second Onsite Cheat Sheet (Adapting to New Problem Statements)

When DTDL assigns a new problem statement onsite, use these 3 simple extension steps:

### 1. Define a New Tool (`backend/tools/telecom_tools.py`)
```python
from langchain_core.tools import tool

@tool
def my_custom_tool(query_param: str) -> str:
    """Clear docstring telling the LLM when and how to call this tool."""
    return json.dumps({"status": "success", "data": query_param})
```

### 2. Create a Worker Agent Node (`backend/agents/multi_agent_system.py`)
```python
def my_new_agent_node(state: AgentState):
    agent_llm = llm.bind_tools([my_custom_tool])
    system_prompt = "You are the DTDL Specialist Agent..."
    response = agent_llm.invoke([SystemMessage(content=system_prompt)] + state["messages"])
    return {"messages": [response], "active_agent": "my_new_agent"}
```

### 3. Connect Node to the StateGraph
```python
workflow.add_node("my_new_agent", my_new_agent_node)
workflow.add_conditional_edges(
    "supervisor",
    lambda state: state["next"],
    {"my_new_agent": "my_new_agent", "FINISH": END}
)
```

---

## 🔑 Quick Setup & Run Instructions

### Option A: Native Python Execution (Recommended for Live Demo)
1. **Configure API Keys** (`.env`):
   ```env
   GROQ_API_KEY=gsk_your_groq_api_key_here
   # OR
   GEMINI_API_KEY=AIzaSy_your_gemini_api_key_here
   ```

2. **Launch Server**:
   ```bash
   python start_server.py
   ```

3. **Open Web Browser**: Navigate to [http://localhost:8000](http://localhost:8000)

---

### Option B: Docker Container Deployment (Enterprise Option)
If judges ask for containerized execution:
```bash
docker-compose up --build
```
The application will automatically build the container image and expose port `8000`.


---

## 💡 Live Demo Walkthrough for Judges

1. **Broadband Diagnostics**: Click *"📡 Diagnose WiFi Router"*. Watch the UI highlight the `Network Agent`, run router pings, identify Channel 6 congestion, and optimize to Channel 11.
2. **Human-In-The-Loop Billing Refund**: Click *"💳 Investigate €25 Bill Charge"*. Watch the `Billing Agent` inspect the invoice, discover the FIFA 4K Pass charge, and trigger the **Human Approval Required** banner for one-click approval.
3. **RAG Knowledge Search**: Click *"📖 RAG Knowledge Search"*. Watch the agent invoke `retrieve_kb_articles` to fetch SLA policies and streaming guidelines.
4. **Plan Advisor**: Click *"🚀 Recommend 5G & TV Pass"*. Watch the `Plan Advisor` search the product catalog and present tailored tariff bundles.
