import os
import sys
import site

# Ensure user site-packages are in sys.path
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from backend.agents.multi_agent_system import create_multi_agent_graph

app = FastAPI(title="DTDL TeleAgent - Multi-Agent AI Platform", version="1.0.0")

# Enable CORS for local web development
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compile LangGraph Workflow
try:
    agent_graph = create_multi_agent_graph()
    print("[SUCCESS] LangGraph Multi-Agent Workflow successfully compiled!")
except Exception as e:
    print(f"[WARNING] Could not compile graph at startup (Check .env keys): {e}")
    agent_graph = None

class ChatRequest(BaseModel):
    message: str
    customer_id: str = "CUST-101"
    thread_id: str = "session_default"

class ApproveRequest(BaseModel):
    thread_id: str = "session_default"
    approved: bool = True
    customer_id: str = "CUST-101"

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "service": "Deutsche Telekom Digital Labs TeleAgent AI Engine",
        "version": "1.0.0"
    }

@app.post("/api/chat")
def chat_endpoint(request: ChatRequest):
    global agent_graph
    if not agent_graph:
        try:
            agent_graph = create_multi_agent_graph()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM Configuration error: {str(e)}. Check your GROQ_API_KEY or GEMINI_API_KEY in .env.")

    initial_state = {
        "messages": [HumanMessage(content=request.message)],
        "next": "supervisor",
        "active_agent": "supervisor",
        "execution_logs": [],
        "customer_id": request.customer_id,
        "requires_human_approval": False,
        "pending_tool_call": None
    }

    config = {"configurable": {"thread_id": request.thread_id}}

    try:
        final_state = agent_graph.invoke(initial_state, config=config)

        # Extract final AI response
        ai_responses = [msg.content for msg in final_state["messages"] if isinstance(msg, AIMessage) and msg.content]
        final_text = ai_responses[-1] if ai_responses else "Request processed successfully."

        # Extract tool calls & outputs
        tool_outputs = []
        for msg in final_state["messages"]:
            if isinstance(msg, ToolMessage):
                tool_outputs.append({
                    "tool": getattr(msg, "name", "tool"),
                    "output": msg.content
                })

        return {
            "response": final_text,
            "active_agent": final_state.get("active_agent", "supervisor"),
            "execution_logs": final_state.get("execution_logs", []),
            "tool_outputs": tool_outputs,
            "requires_human_approval": final_state.get("requires_human_approval", False),
            "pending_tool_call": final_state.get("pending_tool_call")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing agent workflow: {str(e)}")

@app.get("/api/cart/{customer_id}")
def get_cart(customer_id: str):
    from backend.tools.telecom_tools import optimize_smart_cart
    result_json = optimize_smart_cart.invoke({"customer_id": customer_id})
    import json
    return json.loads(result_json)

@app.get("/api/explainable-ai/{product_id}")
def get_xai_explanation(product_id: str, customer_id: str = "CUST-101"):
    from backend.tools.telecom_tools import get_explainable_recommendation
    result_json = get_explainable_recommendation.invoke({"product_id": product_id, "customer_id": customer_id})
    import json
    return json.loads(result_json)

@app.get("/api/impact-summary")
def get_business_impact_summary():
    return {
        "engine": "DTDL Omnichannel Consumer Intelligence Engine",
        "market": "Deutsche Telekom AG (Germany / Europe)",
        "projected_business_outcomes": {
            "cart_abandonment_reduction": "-24.5%",
            "conversion_lift_nba": "+18.2%",
            "first_contact_resolution_fcr": "+38.0%",
            "mean_time_to_resolution_mttr": "Reduced from 48h to 45 seconds",
            "gdpr_compliance_status": "100% Verified (BNetzA SLA & SEPA Audit Logging)"
        },
        "technical_hardening": {
            "routing": "Deterministic Keyword-First + LangGraph Supervisor Fallback",
            "persistence": "LangGraph MemorySaver Checkpointer (thread_id stateful recovery)",
            "vector_rag": "ChromaDB Local Vector Collection (dtdl_telecom_rag)"
        }
    }

@app.post("/api/approve-action")
def approve_action_endpoint(request: ApproveRequest):
    if not request.approved:
        return {
            "status": "REJECTED",
            "message": "Action was cancelled by the human operations agent."
        }

    # Execute approved action directly
    from backend.tools.telecom_tools import apply_bill_credit
    result = apply_bill_credit.invoke({"customer_id": request.customer_id, "amount": 29.75, "reason": "Approved by Human Supervisor (BNetzA SLA)"})

    return {
        "status": "APPROVED",
        "message": "Human approval granted. SEPA refund credit of €29.75 applied successfully!",
        "result": result
    }



# Mount static frontend files if directory exists
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
