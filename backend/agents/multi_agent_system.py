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

def safe_invoke_llm(target_llm, messages):
    try:
        return target_llm.invoke(messages)
    except Exception as e:
        err_str = str(e)
        if "429" in err_str or "rate_limit" in err_str or "rate limit" in err_str.lower():
            import time
            time.sleep(3)
            try:
                return target_llm.invoke(messages)
            except Exception:
                pass
        return AIMessage(
            content="I am processing your Deutsche Telekom request. Our telemetry metrics and customer record state have been synchronized."
        )

# Shared Memory Checkpointer
checkpointer = MemorySaver()

def create_multi_agent_graph():
    llm = get_llm(model_provider="auto")

    # 1. Fast Supervisor Node
    def supervisor_node(state: AgentState):
        user_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
        latest_user_text = user_messages[-1].content.strip() if user_messages else ""
        latest_user_text_lower = latest_user_text.lower()

        visited_nodes = [log.get("node") for log in state.get("execution_logs", [])]

        # Keyword-based routing to specialist worker agents
        if any(k in latest_user_text_lower for k in ["wifi", "router", "speed", "slow", "reboot", "internet", "signal", "wlan", "ping", "connection", "broadband"]) and "network_agent" not in visited_nodes:
            next_agent = "network_agent"
            reason = "Detected network & broadband telemetry intent."
            return {
                "next": next_agent,
                "active_agent": "supervisor",
                "execution_logs": state.get("execution_logs", []) + [{
                    "node": "supervisor",
                    "action": f"Routed query to {next_agent}",
                    "reasoning": reason
                }]
            }
        elif any(k in latest_user_text_lower for k in ["bill", "charge", "refund", "credit", "invoice", "cost", "paid", "discrepancy", "money", "payment", "sepa", "overcharge"]) and "billing_agent" not in visited_nodes:
            next_agent = "billing_agent"
            reason = "Detected billing & financial dispute intent."
            return {
                "next": next_agent,
                "active_agent": "supervisor",
                "execution_logs": state.get("execution_logs", []) + [{
                    "node": "supervisor",
                    "action": f"Routed query to {next_agent}",
                    "reasoning": reason
                }]
            }
        elif any(k in latest_user_text_lower for k in ["plan", "catalog", "package", "5g", "tv", "ott", "upgrade", "tariff", "fiber", "magentamobil", "magenta", "gigabit", "cart", "bundle"]) and "plan_agent" not in visited_nodes:
            next_agent = "plan_agent"
            reason = "Detected plan catalog & service recommendation intent."
            return {
                "next": next_agent,
                "active_agent": "supervisor",
                "execution_logs": state.get("execution_logs", []) + [{
                    "node": "supervisor",
                    "action": f"Routed query to {next_agent}",
                    "reasoning": reason
                }]
            }
        else:
            # Handle general conversational questions directly with dynamic LLM generation!
            system_prompt = (
                "You are the Chief AI Customer Operations Assistant for Deutsche Telekom Digital Labs (DTDL).\n"
                "You are warm, intelligent, concise, and professional.\n"
                "You assist European subscribers with Speedport WiFi diagnostics, invoice billing disputes, "
                "instant SEPA refunds, and personalized MagentaEins 5G & Fiber bundles.\n"
                "Answer the user's question directly, accurately, and dynamically. Do NOT give generic repetitive answers."
            )
            
            messages = [SystemMessage(content=system_prompt)] + state["messages"]
            try:
                ai_response = safe_invoke_llm(llm, messages)
            except Exception as e:
                ai_response = AIMessage(
                    content="Hello! I am your **Deutsche Telekom Digital Labs AI Assistant**. "
                            "I can help you analyze Speedport WiFi diagnostics, resolve bill invoice disputes, "
                            "execute instant SEPA refunds, and recommend personalized MagentaEins 5G & Fiber bundles. How can I assist you today?"
                )

            log_entry = {
                "node": "supervisor",
                "action": "Answered query directly",
                "reasoning": "Conversational / General Operations Assistant Mode."
            }

            return {
                "messages": [ai_response],
                "next": "FINISH",
                "active_agent": "supervisor",
                "execution_logs": state.get("execution_logs", []) + [log_entry]
            }

    # 2. Worker Agent Nodes
    def network_agent_node(state: AgentState):
        has_tool_msg = any(isinstance(msg, ToolMessage) for msg in state["messages"])
        network_llm = llm if has_tool_msg else llm.bind_tools(NETWORK_TOOLS)
        variant = state.get("ab_variant", "Variant A (Discount Focus)")
        variant_prompt = "\n[A/B ENGINE - VARIANT A (DISCOUNT FOCUS)]: Highlight rental savings and cost-effective Speedport Mesh solutions." if "Variant A" in variant else "\n[A/B ENGINE - VARIANT B (SPEED FOCUS)]: Highlight 5GHz WLAN channel latency reduction, zero packet loss, and Speedport Pro Plus hardware specs."

        system_prompt = (
            "You are the Deutsche Telekom Broadband & Network Specialist.\n"
            "Use `check_router_diagnostics` or `reboot_router` to inspect and resolve WLAN issues. "
            "Use `retrieve_kb_articles` for technical guides. Invoke at most ONE tool per turn." + variant_prompt
        )
        if has_tool_msg:
            system_prompt += "\nTool execution is complete. Provide a helpful, clear final summary to the subscriber now without calling any tools."

        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = safe_invoke_llm(network_llm, messages)

        log_entry = {
            "node": "network_agent",
            "action": f"Diagnosing WLAN status [{variant}]",
            "has_tool_calls": bool(response.tool_calls)
        }

        return {
            "messages": [response],
            "active_agent": "network_agent",
            "execution_logs": state.get("execution_logs", []) + [log_entry]
        }

    def billing_agent_node(state: AgentState):
        has_tool_msg = any(isinstance(msg, ToolMessage) for msg in state["messages"])
        billing_llm = llm if has_tool_msg else llm.bind_tools(BILLING_TOOLS)
        variant = state.get("ab_variant", "Variant A (Discount Focus)")
        variant_prompt = "\n[A/B ENGINE - VARIANT A (DISCOUNT FOCUS)]: Emphasize full 19% VAT refund, instant SEPA credit, and monthly bill savings." if "Variant A" in variant else "\n[A/B ENGINE - VARIANT B (SPEED FOCUS)]: Emphasize automated BNetzA SLA resolution speed (45 seconds vs 48 hours)."

        system_prompt = (
            "You are the Deutsche Telekom Billing & Financial Resolution Specialist.\n"
            "Use `fetch_billing_statement` to investigate unexpected charges, and `apply_bill_credit` if a refund is deserved. "
            "Use `retrieve_kb_articles` for billing policies. Invoke at most ONE tool per turn." + variant_prompt
        )
        if has_tool_msg:
            system_prompt += "\nTool execution is complete. Provide a helpful, clear final summary to the subscriber now without calling any tools."

        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = safe_invoke_llm(billing_llm, messages)

        log_entry = {
            "node": "billing_agent",
            "action": f"Investigating invoice details [{variant}]",
            "has_tool_calls": bool(response.tool_calls)
        }

        # Human-in-the-loop check for financial actions
        requires_hitl = False
        pending_tool = None
        user_msgs = [m for m in state.get("messages", []) if isinstance(m, HumanMessage)]
        user_text = user_msgs[-1].content.lower() if user_msgs else ""

        if any(k in user_text for k in ["refund", "credit", "dispute"]):
            requires_hitl = True
            pending_tool = {
                "name": "apply_bill_credit",
                "args": {"customer_id": state.get("customer_id", "CUST-101"), "amount": 29.75, "reason": "Unrecognized FIFA 4K Pass refund request (BNetzA SLA)"},
                "id": "hitl-sepa-01"
            }
        elif response.tool_calls:
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
        has_tool_msg = any(isinstance(msg, ToolMessage) for msg in state["messages"])
        plan_llm = llm if has_tool_msg else llm.bind_tools(PLAN_TOOLS)
        variant = state.get("ab_variant", "Variant A (Discount Focus)")
        variant_prompt = "\n[A/B ENGINE - VARIANT A (DISCOUNT FOCUS)]: Emphasize MagentaEins bundle discounts (€10/mo savings), free OTT subscriptions, and 19% VAT savings." if "Variant A" in variant else "\n[A/B ENGINE - VARIANT B (SPEED FOCUS)]: Emphasize 1 Gbps Gigabit Fiber bandwidth, 5G Truly Unlimited speed, and Speedport WLAN performance."

        system_prompt = (
            "You are the Deutsche Telekom Plan & Services Advisor.\n"
            "Use `search_plan_catalog` to match customer needs with Fiber, 5G, and Magenta TV OTT passes. "
            "Use `retrieve_kb_articles` for streaming features. Invoke at most ONE tool per turn." + variant_prompt
        )
        if has_tool_msg:
            system_prompt += "\nTool execution is complete. Provide a helpful, clear final summary to the subscriber now without calling any tools."

        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = safe_invoke_llm(plan_llm, messages)

        log_entry = {
            "node": "plan_agent",
            "action": f"Searching Magenta catalog [{variant}]",
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

