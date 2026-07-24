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
from typing import Literal, Optional

from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from backend.agents.multi_agent_system import create_multi_agent_graph
from backend.services.checkout_service import (
    get_checkout_preview,
    complete_checkout,
    log_abandonment_nudge,
    get_checkout_events,
)

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

class ApproveRequest(BaseModel):
    thread_id: str = "session_default"
    approved: bool = True
    customer_id: str = "CUST-101"

class CheckoutCompleteRequest(BaseModel):
    customer_id: str = "CUST-101"
    payment_method: Literal["upi", "card", "netbanking"] = "upi"
    upi_id: Optional[str] = None
    channel: str = "OneShop Web"

class AbandonmentNudgeRequest(BaseModel):
    customer_id: str = "CUST-101"
    channel: str = "OneShop Web"
    seconds_open: int = 30

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

    config = {"configurable": {"thread_id": request.thread_id}}

    prior_len = 0
    try:
        snapshot = agent_graph.get_state(config)
        if snapshot and snapshot.values:
            prior_len = len(snapshot.values.get("messages", []))
    except Exception:
        prior_len = 0

    initial_state = {
        "messages": [HumanMessage(content=request.message)],
        "next": "supervisor",
        "active_agent": "supervisor",
        "execution_logs": [],
        "customer_id": request.customer_id,
        "requires_human_approval": False,
        "pending_tool_call": None,
    }

    try:
        final_state = agent_graph.invoke(initial_state, config=config)

        all_messages = final_state["messages"]
        new_messages = all_messages[prior_len:]

        ai_responses = [
            msg.content for msg in new_messages
            if isinstance(msg, AIMessage) and msg.content
        ]
        final_text = ai_responses[-1] if ai_responses else "I couldn't generate a response. Please try again."

        tool_outputs = []
        for msg in new_messages:
            if isinstance(msg, ToolMessage):
                tool_outputs.append({
                    "tool": getattr(msg, "name", "tool"),
                    "output": msg.content,
                })

        return {
            "response": final_text,
            "active_agent": final_state.get("active_agent", "supervisor"),
            "execution_logs": final_state.get("execution_logs", []),
            "tool_outputs": tool_outputs,
            "requires_human_approval": final_state.get("requires_human_approval", False),
            "pending_tool_call": final_state.get("pending_tool_call"),
            "thread_id": request.thread_id,
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

@app.get("/api/checkout/preview/{customer_id}")
def checkout_preview(customer_id: str):
    try:
        return get_checkout_preview(customer_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/checkout/complete")
def checkout_complete(request: CheckoutCompleteRequest):
    try:
        return complete_checkout(
            customer_id=request.customer_id,
            payment_method=request.payment_method,
            upi_id=request.upi_id,
            channel=request.channel,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/checkout/abandonment-nudge")
def checkout_abandonment_nudge(request: AbandonmentNudgeRequest):
    return log_abandonment_nudge(
        customer_id=request.customer_id,
        channel=request.channel,
        seconds_open=request.seconds_open,
    )

@app.get("/api/checkout/events")
def checkout_events(customer_id: Optional[str] = None):
    return get_checkout_events(customer_id)

@app.post("/api/approve-action")
def approve_action_endpoint(request: ApproveRequest):
    if not request.approved:
        return {
            "status": "REJECTED",
            "message": "Action was cancelled by the human operations agent."
        }

    # Execute approved action directly
    from backend.tools.telecom_tools import apply_bill_credit
    result = apply_bill_credit.invoke({"customer_id": request.customer_id, "amount": 500.0, "reason": "Approved by Human Supervisor"})

    return {
        "status": "APPROVED",
        "message": "Human approval granted. Refund credit of ₹500 applied successfully!",
        "result": result
    }


# Mount static frontend files if directory exists
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
