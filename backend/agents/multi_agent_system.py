from typing import Literal
from pydantic import BaseModel, Field

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from backend.config import get_llm
from backend.agents.state import AgentState
from backend.tools.telecom_tools import (
    MOCK_CUSTOMERS,
    NETWORK_TOOLS,
    BILLING_TOOLS,
    PLAN_TOOLS,
    ALL_TOOLS,
)


class RouterResponse(BaseModel):
    next_step: Literal["network_agent", "billing_agent", "plan_agent", "chat_agent"] = Field(
        description=(
            "Specialist agent to handle the request. "
            "Use chat_agent for greetings, identity questions, and general conversation."
        )
    )
    reasoning: str = Field(
        description="Brief explanation of why this routing decision was made."
    )


checkpointer = MemorySaver()


def format_customer_context(customer_id: str) -> str:
    customer = MOCK_CUSTOMERS.get(customer_id, MOCK_CUSTOMERS["CUST-101"])
    return (
        f"Current subscriber profile:\n"
        f"- Customer ID: {customer_id}\n"
        f"- Name: {customer['name']}\n"
        f"- Location: {customer.get('city', 'N/A')}\n"
        f"- Provider: {customer.get('provider', 'N/A')}\n"
        f"- Plan: {customer.get('plan', 'N/A')}\n"
        f"- Loyalty tier: {customer.get('loyalty_tier', 'N/A')}\n"
        f"- Last bill: {customer.get('last_bill_amount', 'N/A')}\n"
        f"- WiFi health: {customer.get('wifi_health', 'N/A')}\n"
    )


def create_multi_agent_graph():
    llm = get_llm(model_provider="auto")

    def supervisor_node(state: AgentState):
        customer_id = state.get("customer_id", "CUST-101")
        customer_ctx = format_customer_context(customer_id)

        system_prompt = (
            "You are the Chief Customer Operations Supervisor for Deutsche Telekom Digital Labs.\n"
            f"{customer_ctx}\n"
            "Route the user's latest message to exactly ONE worker agent:\n"
            "1. network_agent — WiFi speed, router status, reboot, diagnostics, internet connectivity.\n"
            "2. billing_agent — bill breakdowns, extra charges, invoice disputes, refunds, credits.\n"
            "3. plan_agent — 5G/mobile packages, fiber upgrades, Magenta TV passes, catalog search.\n"
            "4. chat_agent — greetings, small talk, 'who am I' / name questions, general help, "
            "anything that does not need telecom tools.\n\n"
            "Prefer specialist agents when the user clearly needs network, billing, or plan operations. "
            "Use chat_agent for conversational and identity questions."
        )

        messages = [SystemMessage(content=system_prompt)] + state["messages"]

        try:
            structured_llm = llm.with_structured_output(RouterResponse)
            res = structured_llm.invoke(messages)
            next_agent = res.next_step
            reason = res.reasoning
        except Exception:
            next_agent = "chat_agent"
            reason = "Routing fallback — conversational agent will respond."

        log_entry = {
            "node": "supervisor",
            "action": f"Routed query to {next_agent}",
            "reasoning": reason,
        }

        return {
            "next": next_agent,
            "active_agent": "supervisor",
            "execution_logs": state.get("execution_logs", []) + [log_entry],
        }

    def chat_agent_node(state: AgentState):
        customer_id = state.get("customer_id", "CUST-101")
        customer_ctx = format_customer_context(customer_id)

        system_prompt = (
            "You are the Deutsche Telekom Digital Labs omnichannel AI assistant.\n"
            f"{customer_ctx}\n"
            "Answer naturally using the subscriber profile above. "
            "If asked their name or identity, use the subscriber name and ID from the profile. "
            "You can help with broadband, billing, and plan questions — suggest specific actions "
            "like diagnosing WiFi, reviewing a bill, or browsing plans when relevant. "
            "Do not invent subscriber details beyond the profile provided."
        )

        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = llm.invoke(messages)

        log_entry = {
            "node": "chat_agent",
            "action": "Generated conversational LLM response",
            "reasoning": "General chat handled by LLM with subscriber context.",
        }

        return {
            "messages": [response],
            "active_agent": "chat_agent",
            "execution_logs": state.get("execution_logs", []) + [log_entry],
        }

    def network_agent_node(state: AgentState):
        customer_id = state.get("customer_id", "CUST-101")
        network_llm = llm.bind_tools(NETWORK_TOOLS)
        system_prompt = (
            "You are the DTDL Broadband & Network Technical Specialist.\n"
            f"{format_customer_context(customer_id)}\n"
            f"Always pass customer_id=\"{customer_id}\" when calling tools.\n"
            "Use check_router_diagnostics and reboot_router to inspect and resolve WiFi issues. "
            "Use retrieve_kb_articles for technical guides. Summarize tool results clearly for the customer."
        )
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = network_llm.invoke(messages)

        log_entry = {
            "node": "network_agent",
            "action": "Diagnosing network status",
            "has_tool_calls": bool(response.tool_calls),
        }

        return {
            "messages": [response],
            "active_agent": "network_agent",
            "execution_logs": state.get("execution_logs", []) + [log_entry],
        }

    def billing_agent_node(state: AgentState):
        customer_id = state.get("customer_id", "CUST-101")
        billing_llm = llm.bind_tools(BILLING_TOOLS)
        system_prompt = (
            "You are the DTDL Billing & Financial Resolution Specialist.\n"
            f"{format_customer_context(customer_id)}\n"
            f"Always pass customer_id=\"{customer_id}\" when calling tools.\n"
            "Use fetch_billing_statement to investigate charges and apply_bill_credit when a refund is deserved. "
            "Use retrieve_kb_articles for billing policies."
        )
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = billing_llm.invoke(messages)

        log_entry = {
            "node": "billing_agent",
            "action": "Investigating invoice details",
            "has_tool_calls": bool(response.tool_calls),
        }

        requires_hitl = False
        pending_tool = None
        if response.tool_calls:
            for tc in response.tool_calls:
                if tc.get("name") == "apply_bill_credit":
                    requires_hitl = True
                    pending_tool = {
                        "name": tc.get("name"),
                        "args": tc.get("args"),
                        "id": tc.get("id"),
                    }
                    break

        return {
            "messages": [response],
            "active_agent": "billing_agent",
            "execution_logs": state.get("execution_logs", []) + [log_entry],
            "requires_human_approval": requires_hitl,
            "pending_tool_call": pending_tool,
        }

    def plan_agent_node(state: AgentState):
        customer_id = state.get("customer_id", "CUST-101")
        plan_llm = llm.bind_tools(PLAN_TOOLS)
        system_prompt = (
            "You are the DTDL Plan & Services Advisor.\n"
            f"{format_customer_context(customer_id)}\n"
            f"Always pass customer_id=\"{customer_id}\" when calling tools.\n"
            "Use search_plan_catalog to match customer needs with Fiber, 5G, and Magenta TV passes. "
            "Use retrieve_kb_articles for streaming features."
        )
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = plan_llm.invoke(messages)

        log_entry = {
            "node": "plan_agent",
            "action": "Searching product catalog",
            "has_tool_calls": bool(response.tool_calls),
        }

        return {
            "messages": [response],
            "active_agent": "plan_agent",
            "execution_logs": state.get("execution_logs", []) + [log_entry],
        }

    tool_node = ToolNode(ALL_TOOLS)

    def should_continue_worker(state: AgentState) -> str:
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    workflow = StateGraph(AgentState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("chat_agent", chat_agent_node)
    workflow.add_node("network_agent", network_agent_node)
    workflow.add_node("billing_agent", billing_agent_node)
    workflow.add_node("plan_agent", plan_agent_node)
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        lambda state: state["next"],
        {
            "chat_agent": "chat_agent",
            "network_agent": "network_agent",
            "billing_agent": "billing_agent",
            "plan_agent": "plan_agent",
        },
    )

    workflow.add_edge("chat_agent", END)
    workflow.add_conditional_edges("network_agent", should_continue_worker, {"tools": "tools", END: END})
    workflow.add_conditional_edges("billing_agent", should_continue_worker, {"tools": "tools", END: END})
    workflow.add_conditional_edges("plan_agent", should_continue_worker, {"tools": "tools", END: END})

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
        },
    )

    return workflow.compile(checkpointer=checkpointer)
