# 🎓 Complete Beginner's Guide & Deep Code Walkthrough
## TeleAgent AI: Deutsche Telekom Omnichannel Consumer Engine (Problem Statement 5)

---

## 📌 Part 1: Core Concepts Explained Simply

If you are new to AI, LLMs, RAG, LangChain, and Agentic AI, here is what each technology means and why we used it:

### 1. What is an LLM (Large Language Model)?
* **Concept**: An LLM (like Groq's Llama 3.3 70B or Google's Gemini 1.5 Flash) is a statistical neural network trained on massive text datasets. It takes input text (a prompt) and predicts the most logical continuation (response).
* **Limitation**: Standard LLMs only *generate text*. They cannot read your personal database, check a live WiFi router, or move money into a bank account by default.

---

### 2. What is Tool Calling / Function Calling?
* **Concept**: Tool calling allows an LLM to invoke external Python code functions.
* **How it works**: We give the LLM a list of Python functions (tools) described with docstrings (e.g. `reboot_router`, `apply_bill_credit`). Instead of generating plain conversational text, the LLM outputs a structured JSON request: `"Run function reboot_router for customer CUST-101"`. Our Python backend executes the tool and gives the live diagnostic result back to the LLM.

---

### 3. What is RAG (Retrieval-Augmented Generation)?
* **Concept**: RAG solves LLM hallucination and knowledge limits by giving the AI an external memory store.
* **Vector Embeddings**: Text is converted into numbers (vectors) representing semantic meaning.
* **Vector Store (ChromaDB)**: A specialized database (ChromaDB) that compares text mathematically. When a user asks *"How do I fix 5GHz WiFi?"*, ChromaDB calculates vector distance and retrieves the top 3 most relevant Deutsche Telekom technical manuals for the AI to read before answering.

---

### 4. What is LangChain vs. LangGraph?
* **LangChain**: A framework for chaining LLMs, prompts, and tools together.
* **LangGraph**: An advanced framework for building **Agentic Workflows as State Machines (Graphs)**.
  * **Nodes**: Individual AI agents or tools (e.g., `Supervisor Node`, `Network Agent Node`).
  * **Edges**: Decision pathways determining which agent speaks next.
  * **State (`AgentState`)**: Shared memory object passed between agents containing message history, active agent logs, customer context, and A/B testing flags.

---

### 5. What is Multi-Agent Architecture (Supervisor Pattern)?
Instead of forcing 1 monolithic AI prompt to handle network diagnostics, billing invoices, product recommendations, and refunds, we build **4 specialized AI Agents**:
1. **Supervisor Router Agent**: The "traffic cop". Analyzes incoming requests and hands off work to the right specialist.
2. **Network Diagnostics Agent**: Specialist for Speedport routers, WLAN 5GHz channel congestion, and soft reboots.
3. **Billing Resolution Agent**: Specialist for 19% German VAT (MwSt.) invoice breakdowns and SEPA refunds.
4. **Commerce & Plan Advisor Agent**: Specialist for Magenta product catalogs, bundle discounts, and Explainable AI (XAI).

---

### 6. What is Human-in-the-Loop (HITL)?
* **Concept**: Never let an autonomous AI execute sensitive financial transactions (like transferring money or issuing credit refunds) without human supervision.
* **Implementation**: When the Billing Agent wants to execute `apply_bill_credit`, it pauses execution and flags `requires_human_approval = True`. The frontend renders a prominent **BNETZA HUMAN APPROVAL REQUIRED** banner. Money moves only when a human operator clicks "Approve".

---

### 7. What is Omnichannel State Persistence (`MemorySaver` / `thread_id`)?
* **Concept**: Customers switch between desktop web (`OneShop`) and mobile app (`OneApp`).
* **Implementation**: LangGraph `MemorySaver` saves session checkpoints using a `thread_id` (e.g. `session_default`). When a user adds an item to cart or reboots a router on `OneShop` and switches to `OneApp`, the exact same state, cart, and chat history load live.

---

### 8. What is A/B Testing & RLHF Preference Feedback?
* **A/B Testing**: The user toggles between `Variant A (Discount Focus)` and `Variant B (Speed Focus)`. The payload passes `ab_variant`, dynamically altering worker agent system prompts to emphasize price savings vs. 1 Gbps speed specs.
* **RLHF (Reinforcement Learning from Human Feedback)**: When users click 👍 or 👎 on assistant responses, `POST /api/feedback` records a `+1.0` or `-1.0` reward signal into the preference log.

---

## 💻 Part 2: Step-by-Step Code Walkthrough

Let's examine the core files in `D:\Hackthon`:

---

### File 1: `backend/agents/state.py` (The Shared Memory Schema)

```python
from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages] # Appends new chat messages to history
    next: str                                            # Next agent node to execute ('network_agent', 'billing_agent', 'FINISH')
    active_agent: str                                    # Name of currently executing agent for UI telemetry
    execution_logs: List[dict]                           # Real-time execution logs shown on UI sidebar
    customer_id: str                                     # Subscriber ID ('CUST-101')
    ab_variant: Optional[str]                            # Active A/B testing variant ('Variant A' or 'Variant B')
    requires_human_approval: Optional[bool]              # HITL flag for financial refund safety
    pending_tool_call: Optional[dict]                    # Details of paused financial tool call awaiting approval
```
* **Explanation**: `AgentState` is the data dictionary that flows through every node in our LangGraph state machine. `Annotated[List[BaseMessage], add_messages]` ensures message history is never overwritten, only appended to.

---

### File 2: `backend/tools/telecom_tools.py` (Domain Datasets, Tools & ChromaDB RAG)

#### 1. Deutsche Telekom European Subscriber Mock Database:
```python
MOCK_CUSTOMERS = {
    "CUST-101": {
        "name": "Alex Mercer",
        "city": "Bonn, Germany (DT HQ Hub)",
        "provider": "Deutsche Telekom AG",
        "plan": "MagentaZuhause XXL Fiber 500 Mbps",
        "router_model": "Speedport Smart 4 Mesh Gateway (5GHz)",
        "last_bill_amount": "€89.20 (incl. 19% German VAT)",
        "standard_bill": "€59.45 (€49.95 + 19% VAT)",
        "discrepancy": "€29.75 extra charge (€25.00 FIFA 4K Pass + €4.75 VAT)",
        "eligible_for_refund": True,
        "iban_sepa": "DE89 3704 0044 0532 0130 00",
        "gdpr_consent": "Verified (BNetzA Compliant)",
        "cart": [
            {"id": "ITEM-01", "name": "MagentaZuhause 500 Mbps Fiber Plan", "price": 49.95, "type": "Plan"},
            {"id": "ITEM-02", "name": "FIFA World Cup 4K Sports Pass", "price": 25.00, "type": "Add-on"}
        ]
    }
}
```

#### 2. ChromaDB Vector Store & Embedding Function (`FastVectorEF`):
```python
class FastVectorEF(EmbeddingFunction):
    def name(self): return "dtdl_fast_vector_ef"
    def __call__(self, input):
        vecs = []
        for text in input:
            tokens = text.lower().split()
            v = [0.0] * 64
            for tok in tokens:
                idx = int(hashlib.md5(tok.encode()).hexdigest(), 16) % 64
                v[idx] += 1.0
            norm = math.sqrt(sum(x * x for x in v)) or 1.0
            vecs.append([x / norm for x in v])
        return vecs
```
* **Explanation**: Generates 64-dimensional term-frequency vectors offline in sub-milliseconds without remote network downloads.

#### 3. RAG Search Tool (`retrieve_kb_articles`):
```python
@tool
def retrieve_kb_articles(query: str) -> str:
    """Queries ChromaDB vector store collection using vector embeddings over DT KB articles."""
    collection = _get_chroma_collection()
    results = collection.query(query_texts=[query], n_results=3)
    ...
```

---

### File 3: `backend/agents/multi_agent_system.py` (Supervisor Router & Worker Nodes)

```python
# Supervisor Router Logic
if any(k in latest_user_text for k in ["wifi", "router", "speed", "reboot"]) and "network_agent" not in visited_nodes:
    next_agent = "network_agent"
elif any(k in latest_user_text for k in ["bill", "charge", "refund", "sepa"]) and "billing_agent" not in visited_nodes:
    next_agent = "billing_agent"
elif any(k in latest_user_text for k in ["plan", "catalog", "5g", "tv"]) and "plan_agent" not in visited_nodes:
    next_agent = "plan_agent"
```
* **Explanation**: Checks incoming user keywords first for sub-millisecond execution. If ambiguous, falls back to LLM structured output classification (`RouterResponse`).

#### Worker Nodes with A/B Prompt Suffixes:
```python
def plan_agent_node(state: AgentState):
    plan_llm = llm.bind_tools(PLAN_TOOLS)
    variant = state.get("ab_variant", "Variant A (Discount Focus)")
    variant_prompt = "\n[A/B ENGINE - VARIANT A (DISCOUNT FOCUS)]: Emphasize MagentaEins bundle discounts (€10/mo savings)." if "Variant A" in variant else "\n[A/B ENGINE - VARIANT B (SPEED FOCUS)]: Emphasize 1 Gbps Gigabit Fiber bandwidth and Speedport WLAN specs."
    
    system_prompt = "You are the Deutsche Telekom Plan & Services Advisor..." + variant_prompt
    response = plan_llm.invoke([SystemMessage(content=system_prompt)] + state["messages"])
    return {"messages": [response], "active_agent": "plan_agent"}
```

---

### File 4: `backend/main.py` (FastAPI Web Endpoints)

```python
class ChatRequest(BaseModel):
    message: str
    customer_id: str = "CUST-101"
    thread_id: str = "session_default"
    ab_variant: str = "Variant A (Discount Focus)"

@app.post("/api/chat")
def chat_endpoint(request: ChatRequest):
    initial_state = {
        "messages": [HumanMessage(content=request.message)],
        "next": "supervisor",
        "customer_id": request.customer_id,
        "ab_variant": request.ab_variant
    }
    config = {"configurable": {"thread_id": request.thread_id}}
    final_state = agent_graph.invoke(initial_state, config=config)
    return {
        "response": ai_responses[-1],
        "active_agent": final_state.get("active_agent"),
        "execution_logs": final_state.get("execution_logs", []),
        "requires_human_approval": final_state.get("requires_human_approval", False)
    }

@app.post("/api/feedback")
def submit_feedback(request: FeedbackRequest):
    return {"status": "logged", "reward_signal": 1.0 if request.rating == "like" else -1.0}
```

---

## 🎯 Part 3: How Problem Statement 5 was Solved

1. **Personalized Discovery**: Pre-loaded subscriber context (Alex Mercer in Bonn) combines device telemetry with ChromaDB vector catalog search.
2. **Conversational Shopping Assistant**: Multi-agent LangGraph supervisor orchestrates diagnostics, bill breakdowns, and shopping advice.
3. **Next Best Action (NBA)**: Proactive banner nudge guides customers toward speed optimizations and Speedport mesh hardware.
4. **Smart Cart & Checkout**: Slide-out cart drawer applies MagentaEins bundle discounts (-€10.00/mo), 19% VAT, and 1-click SEPA Direct Debit checkout.
5. **Omnichannel Experience**: Dual viewports (`OneShop Web` vs `OneApp Mobile Shell`) sync session state in real time via `MemorySaver`.
6. **All 6 Bonus Consideration Features**: Multi-Agent architecture, Real-Time Recommendation engine, Explainable AI (XAI), Continuous Learning (RLHF), A/B Testing framework, and Voice Assistant.

---

### 🚀 Running the Server Locally
```bash
python start_server.py
```
Open browser: `http://localhost:8000`
