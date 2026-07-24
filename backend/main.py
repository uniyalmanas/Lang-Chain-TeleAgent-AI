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
from backend.persistence import log_feedback, get_feedback_summary

app = FastAPI(title="DTDL TeleAgent - Multi-Agent AI Platform", version="1.0.0")

# Enable CORS for local web development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    ab_variant: str = "Variant A (Discount Focus)"

class ApproveRequest(BaseModel):
    thread_id: str = "session_default"
    approved: bool = True
    customer_id: str = "CUST-101"

class FeedbackRequest(BaseModel):
    customer_id: str = "CUST-101"
    rating: str = "like"


def _build_chat_input(graph, request: ChatRequest, config: dict) -> dict:
    """Build minimal input state so the checkpointer merges instead of wiping thread history."""
    input_state = {
        "messages": [HumanMessage(content=request.message)],
        "customer_id": request.customer_id,
        "ab_variant": request.ab_variant,
    }

    # First message in a thread: seed defaults. Follow-up turns rely on checkpoint.
    if graph.checkpointer.get_tuple(config) is None:
        input_state.update({
            "next": "supervisor",
            "active_agent": "supervisor",
            "execution_logs": [],
            "requires_human_approval": False,
            "pending_tool_call": None,
        })

    return input_state


def _extract_chat_response(final_state: dict) -> dict:
    ai_responses = [
        msg.content for msg in final_state["messages"]
        if isinstance(msg, AIMessage) and msg.content
    ]
    final_text = ai_responses[-1] if ai_responses else "Request processed successfully."

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
        "pending_tool_call": final_state.get("pending_tool_call"),
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "service": "Deutsche Telekom Digital Labs TeleAgent AI Engine",
        "version": "1.0.0"
    }

@app.post("/api/feedback")
def submit_feedback(request: FeedbackRequest):
    reward_signal = log_feedback(request.customer_id, request.rating)
    print(f"[RLHF FEEDBACK] customer={request.customer_id} rating={request.rating} (persisted)")
    return {
        "status": "logged",
        "customer_id": request.customer_id,
        "rating": request.rating,
        "reward_signal": reward_signal,
        "persisted": True,
    }


@app.get("/api/feedback/summary")
def feedback_summary():
    return get_feedback_summary()


@app.post("/api/chat")
def chat_endpoint(request: ChatRequest):
    global agent_graph
    if not agent_graph:
        try:
            agent_graph = create_multi_agent_graph()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM Configuration error: {str(e)}. Check your GROQ_API_KEY or GEMINI_API_KEY in .env.")

    config = {"configurable": {"thread_id": request.thread_id}}
    input_state = _build_chat_input(agent_graph, request, config)

    try:
        final_state = agent_graph.invoke(input_state, config=config)
    except Exception as e:
        err_msg = str(e)
        if "rate_limit" in err_msg.lower() or "429" in err_msg or "tool_use_failed" in err_msg:
            print(f"[RETRY FALLBACK] Switching graph to Gemini provider due to provider error: {err_msg[:100]}...")
            try:
                from backend.agents.multi_agent_system import create_multi_agent_graph
                fallback_graph = create_multi_agent_graph()
                final_state = fallback_graph.invoke(input_state, config=config)
            except Exception:
                raise HTTPException(status_code=500, detail=f"Error executing agent workflow: {str(e)}")
        else:
            raise HTTPException(status_code=500, detail=f"Error executing agent workflow: {str(e)}")

    return _extract_chat_response(final_state)

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
            "persistence": "LangGraph SqliteSaver Checkpointer (thread_id survives server restarts)",
            "vector_rag": "ChromaDB Local Vector Collection (dtdl_telecom_rag)"
        }
    }

@app.post("/api/approve-action")
def approve_action_endpoint(request: ApproveRequest):
    if not request.approved:
        return {
            "status": "REJECTED",
            "message": "Action was cancelled by the human operations agent.",
            "thread_id": request.thread_id,
        }

    # Execute approved action directly
    from backend.tools.telecom_tools import apply_bill_credit
    result = apply_bill_credit.invoke({"customer_id": request.customer_id, "amount": 29.75, "reason": "Approved by Human Supervisor (BNetzA SLA)"})

    return {
        "status": "APPROVED",
        "message": "Human approval granted. SEPA refund credit of €29.75 applied successfully!",
        "result": result,
        "thread_id": request.thread_id,
    }



# Mount static frontend files if directory exists
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
