import json
from typing import Literal
from pydantic import BaseModel, Field

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode

from backend.config import get_llm
from backend.agents.state import AgentState
from backend.tools.telecom_tools import (
    NETWORK_TOOLS, BILLING_TOOLS, PLAN_TOOLS, ALL_TOOLS
)

# Supervisor Router Schema for Pydantic structured output
class RouterResponse(BaseModel):
    next_step: Literal["network_agent", "billing_agent", "plan_agent", "FINISH"] = Field(
        description="The next specialized agent to route to, or 'FINISH' if the request is answered."
    )
    reasoning: str = Field(
        description="Brief explanation of why this routing decision was made."
    )

from langgraph.checkpoint.memory import MemorySaver

# Shared Memory Checkpointer
checkpointer = MemorySaver()

def create_multi_agent_graph():
    llm = get_llm(model_provider="auto")

    # 1. Fast Supervisor Node
    def supervisor_node(state: AgentState):
        user_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
        latest_user_text = user_messages[-1].content.lower() if user_messages else ""

        # FAST SHORTCUTS: Don't waste LLM calls for general greetings & plan summaries
        words = set(latest_user_text.split())
        if words.intersection({"hi", "hello", "hey"}) or any(phrase in latest_user_text for phrase in ["who are you", "what can you do"]):
            log_entry = {
                "node": "supervisor",
                "action": "Handled greeting directly",
                "reasoning": "Instant greeting handler."
            }
            greeting_msg = AIMessage(
                content="Hello! I am your **Deutsche Telekom Digital Labs Assistant**. "
                        "I can help you with broadband/WiFi diagnostics, router rebooting, bill invoice breakdowns, "
                        "refund credits, and 5G/Magenta TV plan recommendations. How can I help you today?"
            )
            return {
                "messages": [greeting_msg],
                "next": "FINISH",
                "active_agent": "supervisor",
                "execution_logs": state.get("execution_logs", []) + [log_entry]
            }

        system_prompt = (
            "You are the Chief Customer Operations Supervisor for Deutsche Telekom Digital Labs.\n"
            "Analyze the query and pick the best worker agent:\n"
            "1. 'network_agent': For WiFi speed, router status, reboot, channel congestion, pings.\n"
            "2. 'billing_agent': For bill breakdowns, extra charges, invoice disputes, refunds.\n"
            "3. 'plan_agent': For browsing 5G mobile packages, Fiber broadband upgrades, or Magenta TV passes.\n"
            "4. 'FINISH': If already answered or general statement.\n"
        )

        messages = [SystemMessage(content=system_prompt)] + state["messages"]

        # Fast Keyword Fallback for maximum speed
        if any(k in latest_user_text for k in ["wifi", "router", "speed", "slow", "reboot", "internet", "signal"]):
            next_agent = "network_agent"
            reason = "Detected network telemetry intent."
        elif any(k in latest_user_text for k in ["bill", "charge", "refund", "credit", "invoice", "cost", "paid", "discrepancy"]):
            next_agent = "billing_agent"
            reason = "Detected billing dispute intent."
        elif any(k in latest_user_text for k in ["plan", "catalog", "package", "5g", "tv", "ott", "upgrade", "tariff"]):
            next_agent = "plan_agent"
            reason = "Detected plan catalog intent."
        else:
            try:
                structured_llm = llm.with_structured_output(RouterResponse)
                res = structured_llm.invoke(messages)
                next_agent = res.next_step
                reason = res.reasoning
            except Exception:
                next_agent = "FINISH"
                reason = "Default fallback."

        log_entry = {
            "node": "supervisor",
            "action": f"Routed query to {next_agent}",
            "reasoning": reason
        }

        return {
            "next": next_agent,
            "active_agent": "supervisor",
            "execution_logs": state.get("execution_logs", []) + [log_entry]
        }

    # 2. Worker Agent Nodes
    def network_agent_node(state: AgentState):
        network_llm = llm.bind_tools(NETWORK_TOOLS)
        system_prompt = (
            "You are the DTDL Broadband & Network Technical Specialist.\n"
            "Use `check_router_diagnostics` and `reboot_router` tools to inspect and resolve WiFi issues. "
            "Use `retrieve_kb_articles` for technical guides."
        )
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = network_llm.invoke(messages)

        log_entry = {
            "node": "network_agent",
            "action": "Diagnosing network status",
            "has_tool_calls": bool(response.tool_calls)
        }

        return {
            "messages": [response],
            "active_agent": "network_agent",
            "execution_logs": state.get("execution_logs", []) + [log_entry]
        }

    def billing_agent_node(state: AgentState):
        billing_llm = llm.bind_tools(BILLING_TOOLS)
        system_prompt = (
            "You are the DTDL Billing & Financial Resolution Specialist.\n"
            "Use `fetch_billing_statement` to investigate unexpected charges, and `apply_bill_credit` if a refund is deserved. "
            "Use `retrieve_kb_articles` for billing policies."
        )
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = billing_llm.invoke(messages)

        log_entry = {
            "node": "billing_agent",
            "action": "Investigating invoice details",
            "has_tool_calls": bool(response.tool_calls)
        }

        # Human-in-the-loop check for financial actions
        requires_hitl = False
        pending_tool = None
        if response.tool_calls:
            for tc in response.tool_calls:
                if tc.get("name") == "apply_bill_credit":
                    requires_hitl = True
                    pending_tool = {
                        "name": tc.get("name"),
                        "args": tc.get("args"),
                        "id": tc.get("id")
                    }
                    break

        return {
            "messages": [response],
            "active_agent": "billing_agent",
            "execution_logs": state.get("execution_logs", []) + [log_entry],
            "requires_human_approval": requires_hitl,
            "pending_tool_call": pending_tool
        }

    def plan_agent_node(state: AgentState):
        plan_llm = llm.bind_tools(PLAN_TOOLS)
        system_prompt = (
            "You are the DTDL Plan & Services Advisor.\n"
            "Use `search_plan_catalog` to match customer needs with Fiber, 5G, and Magenta TV OTT passes. "
            "Use `retrieve_kb_articles` for streaming features."
        )
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = plan_llm.invoke(messages)

        log_entry = {
            "node": "plan_agent",
            "action": "Searching product catalog",
            "has_tool_calls": bool(response.tool_calls)
        }

        return {
            "messages": [response],
            "active_agent": "plan_agent",
            "execution_logs": state.get("execution_logs", []) + [log_entry]
        }

    # 3. Tool Execution Node
    tool_node = ToolNode(ALL_TOOLS)

    # 4. Optimized Routing logic: Go straight to END if no more tool calls needed!
    def should_continue_worker(state: AgentState) -> str:
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END  # Direct termination once answer is generated!

    # 5. Build StateGraph
    workflow = StateGraph(AgentState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("network_agent", network_agent_node)
    workflow.add_node("billing_agent", billing_agent_node)
    workflow.add_node("plan_agent", plan_agent_node)
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        lambda state: state["next"],
        {
            "network_agent": "network_agent",
            "billing_agent": "billing_agent",
            "plan_agent": "plan_agent",
            "FINISH": END
        }
    )

    workflow.add_conditional_edges("network_agent", should_continue_worker, {"tools": "tools", END: END})
    workflow.add_conditional_edges("billing_agent", should_continue_worker, {"tools": "tools", END: END})
    workflow.add_conditional_edges("plan_agent", should_continue_worker, {"tools": "tools", END: END})

    # Dynamically return from tool execution to whichever worker agent invoked the tool
    def route_tool_output(state: AgentState) -> str:
        agent = state.get("active_agent", "supervisor")
        if agent in ["network_agent", "billing_agent", "plan_agent"]:
            return agent
        return END

    workflow.add_conditional_edges(
        "tools",
        route_tool_output,
        {
            "network_agent": "network_agent",
            "billing_agent": "billing_agent",
            "plan_agent": "plan_agent",
            "supervisor": END
        }
    )

    return workflow.compile(checkpointer=checkpointer)

